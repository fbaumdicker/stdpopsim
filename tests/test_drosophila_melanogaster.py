"""
Tests for the drosophila_melanogaster data definitions.
"""
import unittest
import io

import msprime

from stdpopsim import drosophila_melanogaster
from qc import drosophlia_melanogaster_qc


class TestGenome(unittest.TestCase):
    """
    Tests for the drosophila_melanogaster genome.
    """
    def test_basic_attributes(self):
        genome = drosophila_melanogaster.genome
        self.assertEqual(genome.species, "drosophila_melanogaster")
        self.assertEqual(genome.default_genetic_map, "Comeron2012_dm6")
        self.assertEqual(len(genome.chromosomes), 8)

    def test_str(self):
        s = str(drosophila_melanogaster.genome)
        self.assertGreater(len(s), 0)
        self.assertIsInstance(s, str)

    def test_chromosome_lengths(self):
        genome = drosophila_melanogaster.genome
        # Numbers from DM6 release
        # `dm6 <https://www.ncbi.nlm.nih.gov/assembly/GCF_000001215.4/>`_.
        self.assertEqual(genome.chromosomes["chr2L"].length, 23513712)
        self.assertEqual(genome.chromosomes["chr2R"].length, 25286936)
        self.assertEqual(genome.chromosomes["chr3L"].length, 28110227)
        self.assertEqual(genome.chromosomes["chr3R"].length, 32079331)
        self.assertEqual(genome.chromosomes["chrX"].length, 23542271)
        self.assertEqual(genome.chromosomes["chr4"].length, 1348131)
        self.assertEqual(genome.chromosomes["chrY"].length, 3667352)


class TestSheehanSongThreeEpoch(unittest.TestCase):
    """
    Basic tests for the SheehanSongThreeEpoch model.
    """

    def test_simulation_runs(self):
        model = drosophila_melanogaster.SheehanSongThreeEpoch()
        samples = [msprime.Sample(population=0, time=0),
                   msprime.Sample(population=0, time=0)]
        ts = msprime.simulate(
            samples=samples, **model.asdict())
        self.assertEqual(ts.num_populations, 1)

    def test_debug_runs(self):
        model = drosophila_melanogaster.SheehanSongThreeEpoch()
        output = io.StringIO()
        model.debug(output)
        s = output.getvalue()
        self.assertGreater(len(s), 0)


class TestLiStephanTwoPopulation(unittest.TestCase):
    """
    Basic tests for the LiStephanTwoPopulation model.
    """

    def test_simulation_runs(self):
        model = drosophila_melanogaster.LiStephanTwoPopulation()
        samples = [msprime.Sample(population=0, time=0),
                   msprime.Sample(population=1, time=0)]
        ts = msprime.simulate(
            samples=samples, **model.asdict())
        self.assertEqual(ts.num_populations, 2)

    def test_debug_runs(self):
        model = drosophila_melanogaster.LiStephanTwoPopulation()
        output = io.StringIO()
        model.debug(output)
        s = output.getvalue()
        self.assertGreater(len(s), 0)

    def test_qc_model_equal(self):
        model = drosophila_melanogaster.LiStephanTwoPopulation()
        model_qc = drosophlia_melanogaster_qc.LiStephanTwoPopulation()
        self.assertTrue(model.equals(model_qc))
