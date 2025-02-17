
Summary
-------

This set of programs allows one to identify transposable element insertions (TEI) in a sequenced sample with respect to an assembled reference. 

The main script jitterbug.py performs this analysis, using a .bam file of mapped reads and the annotation of TEs in the reference.

Additional modules are provided to filter and plot these results, compare tumor/normal pairs as well evaluate predictions from simulated data. 

Citation
--------

If you use this software in your work, please cite:

Jitterbug: somatic and germline transposon insertion detection at single-nucleotide resolution
Elizabeth Hénaff, Luís Zapata, Josep M. Casacuberta, and Stephan Ossowski

BMC Genomics. 2015; 16: 768.
PMCID: PMC4603299


Installation
------------

Dependencies:

Jitterbug requires the following to run:

Python (https://www.python.org/) 
version 2.7 or greater (Jitterbug has not been tested with Python3)

Python modules:
pysam (https://github.com/pysam-developers/pysam)
pybedtools (https://pythonhosted.org/pybedtools/)
psutil (https://pypi.python.org/pypi/psutil)

For the companion scripts to plot results and process tumor/normal pairs, you will need:

matplotlib (http://matplotlib.org/)
matplotlib-venn (https://pypi.python.org/pypi/matplotlib-venn)
numpy (http://www.numpy.org/)

All of these modules are available to install through pip (https://pypi.python.org/pypi/pip)
So, you can run: 
    
    pip install <module_name>

to install each of the above mentioned modules. 

#### note on memory usage
If you are dealing with large input files (i.e. the human genome and not Arabidopsis) you may want to use the

    --pre_filter 
option to pre-select discordant reads with samtools. 
This will write an additional file to disk, but use less memory during runtime. 


Specific requirements:
For Jitterbug to run properly it makes use of a module called y_serial (included).
This module requires that the specified output folder has read and write access for all users.
So remember to set for example chmod -R 777 your_output_folder/ or it will crash

## USE CASE 1: predict TEI in a single sample


### STEP 1.1: run jitterbug.py to identify the candidate TE insertions:

example usage: run with bam file, default everything, write to present directory

    jitterbug.py sample.bam te_annot.gff3

example usage: run with bam file, write to specified directory with specified prefix. Parallelize: use 8 threads, separating by 50 Kbp bins 

    jitterbug.py --numCPUs 8  --bin_size 50000000 --output_prefix /path/to/my/dir/prefix sample.bam te_annot.gff3

example usage: you have added nice unique identifier tags to your gff annotation (like in the hg19 and TAIR10 annotations provided in the data/ folder) and you want those to be reported in the final output. 

    jitterbug.py --TE_name_tag Name --numCPUs 8  --bin_size 50000000 --output_prefix /path/to/my/dir/prefix sample.bam te_annot.gff3


full list of options:

```
usage: jitterbug.py [-h] [-v] [--pre_filter] [-l LIB_NAME] [-d SDEV_MULT]
                    [-o OUTPUT_PREFIX] [-n NUMCPUS] [-b BIN_SIZE] [-q MINMAPQ]
                    [-t TE_NAME_TAG] [-s CONF_LIB_STATS] [-c MIN_CLUSTER_SIZE]
                    [--disc_reads_bam DISC_READS_BAM]
                    mapped_reads TE_annot

positional arguments:
  mapped_reads          reads mapped to reference genome in bam format, sorted
                        by position
  TE_annot              annotation of transposable elements in reference
                        genome, in gff3 format

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         print more output to the terminal
  --pre_filter          pre-filter reads with samtools, and save intermediate
                        filtered read subset
  -l LIB_NAME, --lib_name LIB_NAME
                        sample or library name, to be included in final gff
                        output
  -d SDEV_MULT, --sdev_mult SDEV_MULT
                        use SDEV_MULT*fragment_sdev + fragment_length when
                        calculating insertion intervals. Best you don't touch
                        this.
  -o OUTPUT_PREFIX, --output_prefix OUTPUT_PREFIX
                        prefix of output files. Can be
                        path/to/directory/file_prefix
  -n NUMCPUS, --numCPUs NUMCPUS
                        number of CPUs to use
  -b BIN_SIZE, --bin_size BIN_SIZE
                        If parallelized, size of bins to use, in bp. If
                        numCPUs > 1 and bin_size == 0, will parallelize by
                        entire chromosomes
  -q MINMAPQ, --minMAPQ MINMAPQ
                        minimum read mapping quality to be considered
  -t TE_NAME_TAG, --TE_name_tag TE_NAME_TAG
                        name of tag in TE annotation gff file to use to record
                        inserted TEs
  -s CONF_LIB_STATS, --conf_lib_stats CONF_LIB_STATS
                        tabulated config file that sets the values to use for
                        fragment length and sdev, read length and sdev. 4 tab-
                        deliminated lines: key value, keys
                        are:fragment_length, fragment_length_SD, read_length,
                        read_length_SD
  -c MIN_CLUSTER_SIZE, --min_cluster_size MIN_CLUSTER_SIZE
                        min number of both fwd and rev reads to predict an
                        insertion
  --disc_reads_bam DISC_READS_BAM
                        for debug. Use as input bam file of discordant reads
                        only (generated by running with --pre_filter), and
                        skip the step of perusing the input bam for discordant
                        reads

```


this will generate the following output files:

    <output_prefix>.TE_insertions_paired_clusters.gff3
Annotation in gff3 format of the predicted insertions, with the 9th column's tags describing characteristics of the predictions
    
    <output_prefix>.read_stats.txt
Stats collected on the library: length and standard deviations of the fragments and reads
    
    <output_prefix>.filter_config.txt
Config file with reasonable defaults for the subsequent highly recommended filtering step. These defaults are calculated as a function of the library characteristics
    
    <output_prefix>.run_stats.txt
Stats collected about the run: calculation time, number of processors used
    
    <output_prefix>.TE_insertions_paired_clusters.supporting_clusters.table
Table with infomation on the reads that support each cluster. This table is intended to be easily manipulated with standard *NIX tools in order to, for example, extract the anchor and mate read's sequences for assembly and primer design

The table follows the following format:

Insertion lines: one per predicted insertion site, corresponding to a pair of overlapping clusters, one fwd, one rev

    I       cluster_pair_ID lib     chrom   start   end     num_fwd_reads   num_rev_reads   fwd_span        rev_span        best_sc_pos_st  best_sc_pos_end sc_pos_support

Cluster lines (two per insertion, one fwd and one rev):

    C       cluster_pair_ID lib     direction       start   end     chrom   num_reads       span
 
Read lines (fwd reads consitute the fwd clusters, rev reads the rev clusters)
 the reads' status can be "anchor": those that consitute the cluster, or "mate": are the anchors' mates, which map to a TE

    R       cluster_pair_ID lib     direction       interval_start  interval_end    chrom   status  bam_line


### STEP 1.2: filter results

We recommend you filter the results generated by the previous step 
- to eliminate insertions with poor support
- to eliminate insertions which overlap with Ns in your reference

The first step selects high-confidence insertions based on a set of metrics (see figure Supp2A in related publication). Depending on your application, you might want to have more relaxed filtering criteria: to be sure to recover as many true insertions as possible, knowing those come with more FP, or be stricter and have less TP but with higher confidence. 
The filter_config.txt file output in the first step is automatically generated with reasonable defaults for the given sequencing library. 
these defaults are:
2 < cluster size < 5*coverage
2 < span < mean fragment length
mean read length < interval length < 2*(isize_mean + 2*isize_sdev - (rlen_mean - rlen_sdev))
2 < softclipped support < 5*coverage
pick consistent: name annotation

The second step eliminates false positives that are due to a poorly assembled region. Our experience is that repetitive sequences tend to be more difficult to assemble, and N islands in a draft assembly are often unassembled transposons. For that reason, insertions spanning Ns are likely not insertions in the sample, but absence in the reference sequence of a TE common to both the reference and the sample.

example:

jitterbug_filter_results_func.py -g sample.TE_insertions_paired_clusters.gff3 -c sample.filter_config.txt -o sample.TE_insertions_paired_clusters.filtered.gff3

intersectBed -a sample.TE_insertions_paired_clusters.filtered.gff3 -b N_annot.gff3 -v > sample.TE_insertions_paired_clusters.filtered.noNs.gff3

(intersectBed is part of the BedTools suite, which you can download at https://github.com/arq5x/bedtools2)

usage: jitterbug_filter_results_func.py [-h] [-g GFF] [-c CONFIG] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -g GFF, --gff GFF     file in gff3 format of TEI generated by Jitterbug
  -c CONFIG, --config CONFIG
                        config file with filtering parameters, generated by
                        Jitterbug
  -o OUTPUT, --output OUTPUT
                        name of output file






## USE CASE 2 : looking for somatic insertions in a tumor/normal pair

Included in this package is a module that performs the comparison of a ND/TD pair of samples. 

### STEP 2.1: run Jitterbug on ND and TD samples separately

Run Jitterbug and filter results as described above. 

### STEP 2.2: Identify insertions present in TD which are absent in ND

The goal is to identify somatic insertions: that are present in the tumor sample (ND) and absent from the normal sample (TD). This is done in two steps: 

- take the high-confidence predictions (ie, filtered) from TD and compare them to the whole set (ie, unfiltered) of ND TEI. 

- for those that remain, inspect the ND bam to be sure that the absence of that TEI is not due to low coverage, or to a FP. more than 1% discordant reads in a 200bp window around that locus is taken to be a FP. 

example:

    process_ND_TD.py --TD_F tumor.TE_insertions_paired_clusters.filtered.noNs.gff3 --ND normal.TE_insertions_paired_clusters.gff3 -b normal.bam -o tumor.somatic.TEI.gff3

```
usage: process_ND_TD.py [-h] [--TD_F TD_F] [--ND ND] [-b ND_BAM]
                        [-o OUTPUT_PREFIX]

optional arguments:
  -h, --help            show this help message and exit
  --TD_F TD_F           file in gff3 format of TEI (generated by Jitterbug) in
                        TUMOR sample, FILTERED
  --ND ND               file in gff3 format of TEI (generated by Jitterbug) in
                        NORMAL sample, NOT FILTERED
  -b ND_BAM, --ND_bam ND_BAM
                        bam file of mapped reads from NORMAL sample
  -o OUTPUT_PREFIX, --output_prefix OUTPUT_PREFIX
                        prefix for output file

```

the output are:
- pdf venn diagrams of the intersections of TD filtered and ND unfiltered (Tf and N)
- a gff file annotating the insertions present in Tf but not in N, as well as a table that consists of the same gff annotations followed by a few columns describing the sequence context (+/- 100 bp) surrounding the insertion interval: counting repetitive reads, discordant reads, etc (the header line of the file explains these columns)

the last column is a flag: PUTATIVE-SOM if less than 50% of the reads in that interval are not discordant (meaning it might be a somatic insertion in the tumor) and NON-SOM if not


## USE CASE 3: leverage multiple samples for multi-sample calling
If you have multiple samples, you can refine the calls in each by recovering low-confidence calls (that were excluded by the chosen filtering criteria) that are present as a high-confidence call in another one of your samples. 

The workflow is to: 
- run jitterbug on all your samples
- filter the results
- concatenate and merge the filtered results into a set of unified polymorphic loci
- for each of your samples, pull out from the raw set of call any that overlaps your set of polymorphic loci. This is the "recovered" set of call, which will include those that would have 
passed the filtering anyway, and those that would have been excluded but are found as high-confidence in any one of your other samples. 

The script supplied in the tools/ directory inplements this: 
```
multisample_caller.sh

Usage:

multisample_caller.sh dir_of_unfiltered_calls dir_of_filtered_calls output_prefix
```

This will output a set of files, one for each file in dir_of_unfiltered_calls, with 'sample_name' being parsed from the file name:

```
<output_prefix>.<sample_name>.recovered.gff3
```


Known issues
------------

- Large input bams (>40X coverage for the human genome) can lead to high memory usage. To avoid this, you can use the pre_filtering option:
```
  --pre_filter
```



- Jitterbug only accepts GFF3 format TE annotations. If you have an annotation in BED format, you can convert it using: (assuming the fourth column is the name)

```
awk 'BEGIN{OFS="\t"}{print $1, ".", ".", $2, $3, ".", "+" , "." , "Name="$4}' annot.bed > annot.gff3
```



## Possible subsequent analyses


### Verify inserts by PCR and/or sequence the inserted TE


 Once you have predicted TEI in your sample, you might want to verify them by PCR. We recommend assembling the discordant reads that predicted a given insertion to reconstruct the border of the TE and the sequence flanking it's insertion site in order to design primers. Indeed, there might be a few SNPs between your sample and the reference that would not impede mapping of the read but that would preclude binding of the oligo. 

To do that, you can:

- extract the reads consisting the forward and reverse clusters:

for a a cluster id X, do:
```
less sample.table | awk '$1 == "R"' | grep -w X | grep fwd | awk '{print ">"$2"_"$4"_"$8"_"$12"\n"$19}'> clusterX.fwd.reads.fa
less sample.table | awk '$1 == "R"' | grep -w X | grep rev | awk '{print ">"$2"_"$4"_"$8"_"$12"\n"$19}'> clusterX.rev.reads.fa
```
we then recommend assembling these with a program such as CAP3 (http://doua.prabi.fr/software/cap3)

you can then design primers flanking the insert (p1,p4) and within the insert (p2,p3)

```
FWD cluster assembly                                                  REV cluster assembly 
================_genome_===================########_TE_#########  //  ####_TE_##############===========_genome_===================
                                >>p1>>           <<p2<<                            >>p3>>     <<p4<<                  
```
p1/p2 or p3/p4 can be used to verify the presence of the insert

p1/p4 can be used to:
- check for the presence of the absence allele: if the length of the amplified product corresponds to that of their distance in the reference
- sequence the insert (PCR has to be adjusted for long amplicons)


### Identify target site duplications:

To identify target site duplications, you can extract and assemble the reads as described above and then scan them for direct repeats that occur just once at the predicted insertion site. 



