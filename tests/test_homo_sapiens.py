"""
Tests for the human data definitions.
"""
import unittest
import io

import msprime

from stdpopsim import homo_sapiens
from stdpopsim import genetic_maps


class TestGenome(unittest.TestCase):
    """
    Tests for the human genome.
    """
    def test_basic_attributes(self):
        genome = homo_sapiens.genome
        self.assertEqual(genome.species, "homo_sapiens")
        self.assertEqual(genome.default_genetic_map, "HapmapII_GRCh37")
        self.assertEqual(len(genome.chromosomes), 24)

    def test_str(self):
        s = str(homo_sapiens.genome)
        self.assertGreater(len(s), 0)
        self.assertIsInstance(s, str)

    def test_chromosome_lengths(self):
        genome = homo_sapiens.genome
        # Numbers from https://www.ncbi.nlm.nih.gov/grc/human/data
        # GRCh38.p12
        self.assertEqual(genome.chromosomes["chr1"].length, 248956422)
        self.assertEqual(genome.chromosomes["chr2"].length, 242193529)
        self.assertEqual(genome.chromosomes["chr3"].length, 198295559)
        self.assertEqual(genome.chromosomes["chr4"].length, 190214555)
        self.assertEqual(genome.chromosomes["chr5"].length, 181538259)
        self.assertEqual(genome.chromosomes["chr6"].length, 170805979)
        self.assertEqual(genome.chromosomes["chr7"].length, 159345973)
        self.assertEqual(genome.chromosomes["chr8"].length, 145138636)
        self.assertEqual(genome.chromosomes["chr9"].length, 138394717)
        self.assertEqual(genome.chromosomes["chr10"].length, 133797422)
        self.assertEqual(genome.chromosomes["chr11"].length, 135086622)
        self.assertEqual(genome.chromosomes["chr12"].length, 133275309)
        self.assertEqual(genome.chromosomes["chr13"].length, 114364328)
        self.assertEqual(genome.chromosomes["chr14"].length, 107043718)
        self.assertEqual(genome.chromosomes["chr15"].length, 101991189)
        self.assertEqual(genome.chromosomes["chr16"].length, 90338345)
        self.assertEqual(genome.chromosomes["chr17"].length, 83257441)
        self.assertEqual(genome.chromosomes["chr18"].length, 80373285)
        self.assertEqual(genome.chromosomes["chr19"].length, 58617616)
        self.assertEqual(genome.chromosomes["chr20"].length, 64444167)
        self.assertEqual(genome.chromosomes["chr21"].length, 46709983)
        self.assertEqual(genome.chromosomes["chr22"].length, 50818468)
        self.assertEqual(genome.chromosomes["chrX"].length, 156040895)
        self.assertEqual(genome.chromosomes["chrY"].length, 57227415)

    def test_warning_from_no_mapped_chromosome(self):
        # Test that a known chromosome throws a warning
        # if there is no recombination map associated
        with self.assertWarns(Warning):
            chrom = homo_sapiens.genome.chromosomes["chrY"]
            cm = chrom.recombination_map()
            self.assertIsInstance(cm, msprime.RecombinationMap)

    def test_warning_from_mapped_chromosome(self):
        # Test that a known chromosome can get a
        # recombination map associated with it
        chrom = homo_sapiens.genome.chromosomes["chr1"]
        cm = chrom.recombination_map()
        self.assertIsInstance(cm, msprime.RecombinationMap)

    def test_chromosome_errors(self):
        # Assert that unknown chromosomes throw a KeyError
        with self.assertRaises(KeyError):
            homo_sapiens.genome.chromosomes["jibberish"]


class TestGeneticMap(unittest.TestCase):
    """
    Basic tests for the GeneticMap class
    """

    def test_get_genetic_map(self):
        default_map = homo_sapiens.genome.default_genetic_map
        HapmapII_GRCh37 = genetic_maps.get_genetic_map("homo_sapiens", default_map)
        self.assertIsInstance(HapmapII_GRCh37, genetic_maps.GeneticMap)

    def test_unknown_get_chromosome_map(self):
        default_map = homo_sapiens.genome.default_genetic_map
        HapmapII_GRCh37 = genetic_maps.get_genetic_map("homo_sapiens", default_map)
        with self.assertRaises(ValueError):
            HapmapII_GRCh37.get_chromosome_map("jibberish")

    def test_known_get_chromosome_map(self):
        default_map = homo_sapiens.genome.default_genetic_map
        HapmapII_GRCh37 = genetic_maps.get_genetic_map("homo_sapiens", default_map)
        recombination_map = HapmapII_GRCh37.get_chromosome_map("chr1")
        self.assertIsInstance(recombination_map, msprime.RecombinationMap)


class TestGutenkunstOutOfAfrica(unittest.TestCase):
    """
    Basic tests for the GutenkunstThreePopOutOfAfrica model.
    """

    def test_simulation_runs(self):
        model = homo_sapiens.GutenkunstThreePopOutOfAfrica()
        ts = msprime.simulate(
            samples=[msprime.Sample(pop, 0) for pop in range(3)],
            **model.asdict())
        self.assertEqual(ts.num_populations, 3)

    def test_debug_runs(self):
        model = homo_sapiens.GutenkunstThreePopOutOfAfrica()
        output = io.StringIO()
        model.debug(output)
        s = output.getvalue()
        self.assertGreater(len(s), 0)


class TestTennessenEuropean(unittest.TestCase):
    """
    Basic tests for the TennessenEuropean model.
    """

    def test_simulation_runs(self):
        model = homo_sapiens.TennessenEuropean()
        ts = msprime.simulate(
            samples=[msprime.Sample(0, 0) for _ in range(10)],
            **model.asdict())
        self.assertEqual(ts.num_populations, 1)

    def test_debug_runs(self):
        model = homo_sapiens.TennessenEuropean()
        output = io.StringIO()
        model.debug(output)
        s = output.getvalue()
        self.assertGreater(len(s), 0)
