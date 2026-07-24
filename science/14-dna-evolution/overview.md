---
title: "DNA, Gene Expression, Inheritance, and Evolution"
slug: "14-dna-evolution"
module: "Module 14: DNA, gene expression, inheritance, and evolution"
domain: "science"
status: draft
prerequisites: ["07-chemical-bonding", "13-cells-bioenergetics"]
connections: ["15-ecology-systems", "16-biotechnology"]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

## 1. The central questions

How is the information required to build and maintain a living organism stored, copied, and transmitted across generations? How does this stored information direct the synthesis of functional molecules within a cell? Furthermore, how do changes in this information over time lead to the diversity of life observed on Earth? These questions form the core of molecular biology, genetics, and evolutionary theory. They address the physical basis of heredity, the mechanisms of gene expression, and the population-level dynamics that drive evolutionary change.

## 2. Observable phenomena

The macroscopic diversity of life is underpinned by microscopic molecular processes. Offspring resemble their parents, yet exhibit variation. This inheritance of traits follows predictable patterns, first observed by Gregor Mendel in pea plants. At the cellular level, cells divide and replicate, requiring the exact duplication of their genetic material. When cells differentiate, they express different traits despite containing identical genetic instructions, a phenomenon driven by gene regulation. Over longer timescales, populations of organisms adapt to their environments, and new species emerge, phenomena observable in the fossil record and in the genomic sequences of extant organisms.

## 3. Essential concepts

**Deoxyribonucleic Acid (DNA):** The molecule that carries the genetic instructions for life. It consists of two antiparallel polynucleotide strands coiled into a double helix. Each nucleotide contains a phosphate group, a deoxyribose sugar, and a nitrogenous base (adenine, thymine, cytosine, or guanine) [1].

**Gene:** A specific sequence of DNA nucleotides that encodes the instructions for synthesizing a functional product, typically a protein or an RNA molecule.

**Gene Expression:** The process by which the information encoded in a gene is used to direct the assembly of a protein molecule. It involves two main stages: transcription and translation.

**Allele:** A variant form of a gene. Different alleles can result in different observable traits (phenotypes).

**Genotype and Phenotype:** The genotype is the specific set of alleles an organism possesses. The phenotype is the observable physical or biochemical characteristics of the organism, determined by the interaction of its genotype and the environment.

**Mutation:** A change in the nucleotide sequence of an organism's DNA. Mutations are the ultimate source of genetic variation.

**Natural Selection:** The differential survival and reproduction of individuals due to differences in phenotype. It is a key mechanism of evolution.

**Genetic Drift:** The change in the frequency of an existing gene variant (allele) in a population due to random chance.

## 4. Mechanisms and causal chains

### DNA Replication

DNA replication is semi-conservative, meaning each new double helix consists of one original (template) strand and one newly synthesized strand. The process begins at specific locations called origins of replication. The enzyme helicase unwinds the double helix, breaking the hydrogen bonds between complementary base pairs. Single-strand binding proteins stabilize the unwound strands. Topoisomerase relieves the torsional strain ahead of the replication fork [2].

Because DNA polymerase can only add nucleotides to an existing 3'-OH group, an RNA primase synthesizes a short RNA primer. DNA polymerase III then adds deoxyribonucleotides to the 3' end of the primer, synthesizing the new strand in the 5' to 3' direction. On the leading strand, synthesis is continuous. On the lagging strand, synthesis is discontinuous, occurring in short segments called Okazaki fragments. DNA polymerase I later replaces the RNA primers with DNA, and DNA ligase seals the nicks between the fragments [2].

### Transcription and Translation

Gene expression begins with transcription, where a specific segment of DNA is copied into messenger RNA (mRNA). RNA polymerase binds to a promoter region upstream of the gene, unwinds the DNA, and synthesizes a complementary RNA strand using the template DNA strand. In eukaryotes, the initial pre-mRNA undergoes processing, including the addition of a 5' cap, a 3' poly-A tail, and the splicing out of non-coding regions (introns) [3].

Translation occurs at the ribosome. The mRNA sequence is read in sets of three nucleotides called codons. Each codon specifies a particular amino acid. Transfer RNA (tRNA) molecules act as adaptors; one end contains an anticodon that base-pairs with the mRNA codon, and the other end carries the corresponding amino acid. The ribosome facilitates the formation of peptide bonds between adjacent amino acids, building a polypeptide chain that will fold into a functional protein [4].

### Evolutionary Mechanisms

Evolution is defined as a change in allele frequencies in a population over time. This change is driven by four primary mechanisms:

1.  **Mutation:** Introduces new alleles into the population.
2.  **Natural Selection:** Alleles that confer a survival or reproductive advantage increase in frequency.
3.  **Genetic Drift:** Random fluctuations in allele frequencies, particularly significant in small populations (e.g., bottleneck or founder effects) [5].
4.  **Gene Flow:** The transfer of alleles between populations due to migration.

## 5. Important quantities

| Quantity | Description | Typical Value/Range |
| :--- | :--- | :--- |
| Genome Size | Total amount of DNA contained within one copy of a single genome. | $4.6 \times 10^6$ bp (E. coli), $3.2 \times 10^9$ bp (Human) |
| Mutation Rate | The frequency of new mutations in a single gene or organism over time. | $\sim 10^{-8}$ per base pair per generation (Human) |
| Allele Frequency | The relative frequency of an allele at a particular locus in a population. | $0 \le p \le 1$ |
| Translation Rate | The speed at which a ribosome synthesizes a polypeptide. | $\sim 10-20$ amino acids per second (Prokaryotes) |

## 6. Mathematical models and equations

### The Hardy-Weinberg Principle

The Hardy-Weinberg principle provides a null model for population genetics, describing a population that is not evolving. It states that allele and genotype frequencies in a population will remain constant from generation to generation in the absence of other evolutionary influences (no mutation, random mating, no gene flow, infinite population size, and no selection) [6].

For a gene with two alleles, $A$ and $a$, with frequencies $p$ and $q$ respectively:

$$p + q = 1$$

The expected genotype frequencies are given by the Hardy-Weinberg equation:

$$p^2 + 2pq + q^2 = 1$$

Where:
*   $p^2$ is the frequency of the homozygous dominant genotype ($AA$).
*   $2pq$ is the frequency of the heterozygous genotype ($Aa$).
*   $q^2$ is the frequency of the homozygous recessive genotype ($aa$).

### Population Growth and Selection

The change in allele frequency due to selection can be modeled. If the relative fitness of genotypes $AA$, $Aa$, and $aa$ are $w_{11}$, $w_{12}$, and $w_{22}$ respectively, the mean fitness of the population ($\bar{w}$) is:

$$\bar{w} = p^2w_{11} + 2pqw_{12} + q^2w_{22}$$

The frequency of allele $A$ in the next generation ($p'$) is:

$$p' = \frac{p^2w_{11} + pqw_{12}}{\bar{w}}$$

The change in allele frequency ($\Delta p$) is:

$$\Delta p = p' - p = \frac{pq[p(w_{11} - w_{12}) + q(w_{12} - w_{22})]}{\bar{w}}$$

## 7. Definitions of symbols and units

*   $p$: Frequency of the dominant allele (dimensionless).
*   $q$: Frequency of the recessive allele (dimensionless).
*   $w$: Relative fitness, a measure of reproductive success (dimensionless, $0 \le w \le 1$).
*   $\bar{w}$: Mean fitness of the population (dimensionless).
*   bp: Base pairs, a unit of length for double-stranded nucleic acids.

## 8. Assumptions and approximations

*   **Hardy-Weinberg Equilibrium:** Assumes an infinitely large population, random mating, no mutations, no migration, and no natural selection. In reality, no natural population perfectly meets all these criteria, making it a theoretical baseline.
*   **Mendelian Inheritance:** Assumes independent assortment and segregation of alleles. This is an approximation that fails when genes are closely linked on the same chromosome.
*   **Constant Mutation Rate:** Evolutionary models often assume a constant molecular clock, but mutation rates can vary across different regions of the genome and among different lineages.

## 9. Spatial and temporal scales

*   **Spatial:** Processes range from the nanometer scale (diameter of a DNA double helix is $\sim 2$ nm) to the micrometer scale (cellular organelles like the nucleus and ribosomes) to the macroscopic scale of entire populations and ecosystems.
*   **Temporal:** DNA replication and protein synthesis occur on the scale of seconds to minutes. The lifespan of an organism dictates the generation time (days for bacteria, decades for humans). Evolutionary changes, such as speciation, typically occur over thousands to millions of years.

## 10. Common misconceptions

*   **Misconception:** Evolution is "just a theory" meaning it is a guess. **Correction:** In science, a theory is a well-substantiated explanation of some aspect of the natural world, based on a body of facts that have been repeatedly confirmed through observation and experiment.
*   **Misconception:** Individuals evolve during their lifetime. **Correction:** Populations evolve over generations; individuals do not change their genetic makeup in response to environmental pressures.
*   **Misconception:** Mutations are always harmful. **Correction:** While many mutations are deleterious or neutral, some are beneficial and provide the raw material for adaptation.
*   **Misconception:** Dominant alleles are always the most common in a population. **Correction:** Dominance refers to the expression of the allele in a heterozygote, not its frequency. A dominant allele can be rare (e.g., the allele for Huntington's disease).

## 11. Connections to other modules

*   **07-chemical-bonding:** Understanding hydrogen bonding is crucial for comprehending the specific base-pairing in DNA and the secondary structures of RNA and proteins.
*   **13-cells-bioenergetics:** The processes of DNA replication, transcription, and translation are highly energy-dependent, relying on ATP generated through cellular respiration.
*   **15-ecology-systems:** Population genetics and evolutionary mechanisms are foundational for understanding ecological dynamics, species interactions, and biodiversity.
*   **16-biotechnology:** The principles of DNA structure and gene expression are applied in genetic engineering, PCR, and sequencing technologies.

## 12. Sources

[1] Pray, L. (2008). Discovery of DNA structure and function: Watson and Crick. *Nature Education*, 1(1), 100. http://www.nature.com/scitable/topicpage/discovery-of-dna-structure-and-function-watson-397
[2] Pray, L. (2008). Major molecular events of DNA replication. *Nature Education*, 1(1), 99. http://www.nature.com/scitable/topicpage/major-molecular-events-of-dna-replication-413
[3] Clancy, S. (2008). DNA transcription. *Nature Education*, 1(1), 41. https://www.nature.com/scitable/topicpage/dna-transcription-426/
[4] Clancy, S., & Brown, W. (2008). Translation: DNA to mRNA to Protein. *Nature Education*, 1(1), 101. https://www.nature.com/scitable/topicpage/translation-dna-to-mrna-to-protein-393/
[5] Fowler, S., Roush, R., & Wise, J. (2013). 11.2 Mechanisms of Evolution. In *Concepts of Biology*. OpenStax. https://openstax.org/books/concepts-biology/pages/11-2-mechanisms-of-evolution
[6] OpenStax. (2018). 19.2 Population Genetics. In *Biology for AP® Courses*. OpenStax. https://openstax.org/books/biology-ap-courses/pages/19-2-population-genetics
