"""
Common infrastructure for specifying demographic models.
"""
import sys

import msprime
import numpy as np


# Defaults taken from np.allclose
DEFAULT_ATOL = 1e-05
DEFAULT_RTOL = 1e-08


class UnequalModelsError(Exception):
    """
    Exception raised models by verify_equal to indicate that models are
    not sufficiently close.
    """


def population_configurations_equal(
        pop_configs1, pop_configs2, rtol=DEFAULT_RTOL, atol=DEFAULT_ATOL):
    """
    Returns True if the specified lists of msprime PopulationConfiguration
    objects are equal to the specified tolerances.

    See the :func:`.verify_population_configurations_equal` function for
    details on the assumptions made about the objects.
    """
    try:
        verify_population_configurations_equal(
            pop_configs1, pop_configs2, rtol=rtol, atol=atol)
        return True
    except UnequalModelsError:
        return False


def verify_population_configurations_equal(
        pop_configs1, pop_configs2, rtol=DEFAULT_RTOL, atol=DEFAULT_ATOL):
    """
    Checks if the specified lists of msprime PopulationConfiguration
    objects are equal to the specified tolerances and raises an UnequalModelsError
    otherwise.

    We make some assumptions here to ensure that the models we specify
    are well-defined: (1) The sample size is not set for PopulationConfigurations
    (2) the initial_size is defined. If these assumptions are violated a
    ValueError is raised.
    """
    for pc1, pc2 in zip(pop_configs1, pop_configs2):
        if pc1.sample_size is not None or pc2.sample_size is not None:
            raise ValueError(
                "Models defined in stdpopsim must not use the 'sample_size' "
                "PopulationConfiguration option")
        if pc1.initial_size is None or pc2.initial_size is None:
            raise ValueError(
                "Models defined in stdpopsim must set the initial_size")
    if len(pop_configs1) != len(pop_configs2):
        raise UnequalModelsError("Different numbers of populations")
    initial_size1 = np.array([pc.initial_size for pc in pop_configs1])
    initial_size2 = np.array([pc.initial_size for pc in pop_configs2])
    if not np.allclose(initial_size1, initial_size2, rtol=rtol, atol=atol):
        raise UnequalModelsError("Initial sizes differ")
    growth_rate1 = np.array([pc.growth_rate for pc in pop_configs1])
    growth_rate2 = np.array([pc.growth_rate for pc in pop_configs2])
    if not np.allclose(growth_rate1, growth_rate2, rtol=rtol, atol=atol):
        raise UnequalModelsError("Growth rates differ")


def demographic_events_equal(
        events1, events2, num_populations, rtol=DEFAULT_RTOL, atol=DEFAULT_ATOL):
    """
    Returns True if the specified list of msprime DemographicEvent objects are equal
    to the specified tolerances.
    """
    try:
        verify_demographic_events_equal(
            events1, events2, num_populations, rtol=rtol, atol=atol)
        return True
    except UnequalModelsError:
        return False


def verify_demographic_events_equal(
        events1, events2, num_populations, rtol=DEFAULT_RTOL, atol=DEFAULT_ATOL):
    """
    Checks if the specified list of msprime DemographicEvent objects are equal
    to the specified tolerances and raises a UnequalModelsError otherwise.
    """
    # Get the low-level dictionary representations of the events.
    dicts1 = [event.get_ll_representation(num_populations) for event in events1]
    dicts2 = [event.get_ll_representation(num_populations) for event in events2]
    if len(dicts1) != len(dicts2):
        raise UnequalModelsError("Different numbers of demographic events")
    for d1, d2 in zip(dicts1, dicts2):
        if set(d1.keys()) != set(d2.keys()):
            raise UnequalModelsError("Different types of demographic events")
        for key in d1.keys():
            value1 = d1[key]
            value2 = d2[key]
            if isinstance(value1, float):
                if not np.isclose(value1, value2, rtol=rtol, atol=atol):
                    raise UnequalModelsError("Event {} mismatch: {} != {}".format(
                        key, value1, value2))
            else:
                if value1 != value2:
                    raise UnequalModelsError("Event {} mismatch: {} != {}".format(
                        key, value1, value2))


class Population(object):
    """
    Class recording metadata representing a population in a simulation.

    :ivar name: the name of the population
    :vartype name: str
    :ivar description: a short description of the population
    :vartype description: str
    :ivar sampling_time: an integer value which indicates how many
        generations prior to the present individuals should samples should
        be drawn from this population. If `None`, sampling not allowed from this
        population (default = 0).
    :vartype sampling_time: int
    """
    # TODO change this to use the usual id, name combination
    def __init__(self, name, description, sampling_time=0):
        self.name = name
        self.description = description
        self.sampling_time = sampling_time

    @property
    def allow_samples(self):
        return self.sampling_time is not None

    def asdict(self):
        """
        Returns a dictionary representing the metadata about this population.
        """
        return {"name": self.name, "description": self.description,
                "sampling_time": self.sampling_time}


class Model(object):
    """
    Class representing a simulation model that can be run to output a tree sequence.
    Concrete subclasses must define population_configurations, demographic_events
    and migration_matrix instance variables which define the model.

    :ivar id: The unique identifier for this model. Model IDs should be
        short and memorable, perhaps as an abbreviation of the model's
        name.
    :vartype id: str
    :ivar name: The informal name for this model as it would be used in
        written text, e.g., "Three population Out-of-Africa"
    :vartype informal_name: str
    """
    # TODO the infrastructure here is left over from a structure that
    # rigidly used class definitions as a way to define population
    # models. This contructor should take all the instance variables
    # as parameteters, and we should use factory functions to define
    # the model instances that are added to the catalog rather than
    # subclasses.

    def __init__(self):
        self.population_configurations = []
        self.demographic_events = []
        # Defaults to a single population
        self.migration_matrix = [[0]]
        self.generation_time = None

    @property
    def num_populations(self):
        return len(self.populations)

    @property
    def num_sampling_populations(self):
        return sum(int(pop.allow_samples) for pop in self.populations)

    def equals(self, other, rtol=DEFAULT_RTOL, atol=DEFAULT_ATOL):
        """
        Returns True if this model is equal to the specified model to the
        specified numerical tolerance (as defined by numpy.allclose).

        We use the 'equals' method here rather than the equality operator
        because we need to be able to specifiy the numerical tolerances.
        """
        try:
            self.verify_equal(other, rtol=rtol, atol=atol)
            return True
        except (UnequalModelsError, AttributeError):
            return False

    def verify_equal(self, other, rtol=DEFAULT_RTOL, atol=DEFAULT_ATOL):
        """
        Equivalent to the :func:`.equals` method, but raises a UnequalModelsError if the
        models are not equal rather than returning False.
        """
        mm1 = np.array(self.migration_matrix)
        mm2 = np.array(other.migration_matrix)
        if mm1.shape != mm2.shape:
            raise UnequalModelsError("Migration matrices different shapes")
        if not np.allclose(mm1, mm2, rtol=rtol, atol=atol):
            raise UnequalModelsError("Migration matrices differ")
        verify_population_configurations_equal(
            self.population_configurations, other.population_configurations,
            rtol=rtol, atol=atol)
        verify_demographic_events_equal(
            self.demographic_events, other.demographic_events,
            len(self.population_configurations),
            rtol=rtol, atol=atol)

    def debug(self, out_file=sys.stdout):
        # Use the demography debugger to print out the demographic history
        # that we have just described.
        dd = msprime.DemographyDebugger(
            population_configurations=self.population_configurations,
            migration_matrix=self.migration_matrix,
            demographic_events=self.demographic_events)
        dd.print_history(out_file)

    def get_samples(self, *args):
        """
        Returns a list of msprime.Sample objects as described by the args and
        keyword args. Positional arguments are interpreted as the number of
        samples to take from the given population.

        .. todo:: Add a description how the positional arguments work and
            perhaps link into a section of the tutorial showing it in action.

        """
        samples = []
        for pop_index, n in enumerate(args):
            if self.populations[pop_index].allow_samples:
                sample = msprime.Sample(
                                        pop_index,
                                        time=self.populations[pop_index].sampling_time)
                samples.extend([sample] * n)
            elif n > 0:
                raise ValueError("Samples requested from non-sampling population"
                                 f" {pop_index}")
        return samples


# Reusable generic populations
_pop0 = Population(name="pop0", description="Generic population")
_pop1 = Population(name="pop1", description="Generic population")
_popAnc = Population(name="popAnc", description="Generic ancestral population",
                     sampling_time=None)


class PiecewiseConstantSize(Model):
    """
    Class representing a generic simulation model that can be run to output a
    tree sequence. This is a piecewise constant size model, which allows for
    instantaneous population size change over multiple epochs in a single population.

    :ivar N0: The initial effective population size
    :vartype N0: float
    :ivar args: Each subsequent argument is a tuple (t, N) which gives the
        time at which the size change takes place and the population size.

    The usage is best illustrated by an example:

    .. code-block:: python

        model1 = stdpopsim.PiecewiseConstantSize(N0, (t1, N1)) # One change
        model2 = stdpopsim.PiecewiseConstantSize(N0, (t1, N1), (t2, N2)) # Two changes
    """

    id = "constant"
    name = "Piecewise constant size"
    description = "Piecewise constant size population model over multiple epochs."
    citations = []
    populations = [_pop0]
    author = None
    year = None
    doi = None

    def __init__(self, N0, *args):
        self.population_configurations = [
            msprime.PopulationConfiguration(
                initial_size=N0, metadata=self.populations[0].asdict())
        ]
        self.migration_matrix = [[0]]
        self.demographic_events = []
        for t, N in args:
            self.demographic_events.append(msprime.PopulationParametersChange(
                time=t, initial_size=N, growth_rate=0, population_id=0))


class GenericIM(Model):
    """
    Class representing a generic simulation model that can be run to output a tree
    sequence. A generic isolation with migration model where a single ancestral
    population of size NA splits into two populations of constant size N1
    and N2 time T generations ago, with migration rates M12 and M21 between
    the split populations. Sampling is disallowed in population index 0,
    as this is the ancestral population.

    :ivar NA: The initial ancestral effective population size
    :vartype NA: float
    :ivar N1: The effective population size of population 1
    :vartype N1: float
    :ivar N2: The effective population size of population 2
    :vartype N2: float
    :ivar T: Time of split between populations 1 and 2 (in generations)
    :vartype T: float
    :ivar M12: Migration rate from population 1 to 2
    :vartype M12: float
    :ivar M21: Migration rate from population 2 to 1
    :vartype M21: float


    Example usage:

    .. code-block:: python

        model1 = stdpopsim.GenericIM(NA, N1, N2, T, M12, M21)

    """
    id = "IM"
    name = "Isolation with migration"
    description = """
        A generic isolation with migration model where a single ancestral
        population of size NA splits into two populations of constant size N1
        and N2 time T generations ago, with migration rates M12 and M21 between
        the split populations.
        """
    citations = []
    populations = [_pop0, _pop1, _popAnc]
    author = None
    year = None
    doi = None

    def __init__(self, NA, N1, N2, T, M12, M21):
        self.population_configurations = [
            msprime.PopulationConfiguration(
                initial_size=N1, metadata=self.populations[0].asdict()),
            msprime.PopulationConfiguration(
                initial_size=N2, metadata=self.populations[1].asdict()),
            msprime.PopulationConfiguration(
                initial_size=NA, metadata=self.populations[2].asdict())
        ]
        self.migration_matrix = [[0, M12, 0], [M21, 0, 0], [0, 0, 0]]
        self.demographic_events = [
            msprime.MassMigration(
                time=T, source=0, destination=2, proportion=1),
            msprime.MassMigration(
                time=T, source=1, destination=2, proportion=1)
        ]
