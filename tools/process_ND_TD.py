#!/usr/bin/env python


import sys,argparse
import pysam
import pybedtools as pybed
import matplotlib.pyplot as plt
import numpy as np
from matplotlib_venn import venn3, venn3_circles, venn2, venn2_circles

from GffAnnot import *


def main(argv):


    ##############START argparse version ###############

    parser = argparse.ArgumentParser()

    
    
    parser.add_argument("--TD_F",dest='tdf', help="file in gff3 format of TEI (generated by Jitterbug) in TUMOR sample, FILTERED")
    parser.add_argument("--ND", dest='nd',help="file in gff3 format of TEI (generated by Jitterbug) in NORMAL sample, NOT FILTERED")
    parser.add_argument("-b", "--ND_bam",dest='bam', help="bam file of mapped reads from NORMAL sample")
    parser.add_argument("-o", "--output_prefix",dest='o', help="prefix for output files")
    parser.add_argument("-c","-cfg_file",dest='cfg', help="configuration file")

    args = parser.parse_args()

#    jitterbug_filter_results(args.gff, args.config, args.output)


    ############## END argparse version

    ############## START getopt version 

#    helpString  = "script which takes the Jitterbug predictions for a tumor/normal pair and processes them by:\n\
#                1) intersecting the filtered TD and ND sets and outputing correspondng venn diagrams \n\
#                2) using the supplied bam file, inspecting the loci with putative somatic insertions (in TD only) \n\
#                to determine whether one can rule out a non-reference state (insertion) in ND"
#
#    try:
#        opts, args = getopt.getopt(argv, "h:b:l:s:p:", ["T=", "N=", "TF=", "NF="])
#    except getopt.GetoptError:
#        print helpString
#        sys.exit(2)
#
#
    plot = False
#    
#
#    # Get parameters from command line
#    for opt, arg in opts:
#        if opt == "-h":
#            print helpString
#            sys.exit()
#
#        elif opt == "--T":
#            t_gff = arg
#        # elif opt == "--N":
#        #     n_gff = arg
#
#        elif opt == "--TF":
#            t_F_gff = arg
#        # elif opt == "--NF":
#        #     n_F_gff = arg
#
#        elif opt == "-b":
#            bam_file = arg
#        elif opt == "-l":
#            library_name = arg
#        elif opt == "-s":
#            read_stats_file = arg
#        elif opt == "-p":
#            plot = eval(arg)
#        else:
#            print helpString
#            sys.exit()
#
#    ################ END getopt version ###############

    read_stats = {}
    read_stats_file = args.cfg
    for line in open(read_stats_file):
        line = line.strip()
        tag, val = line.split("\t")
        read_stats[tag] = float(val)
    print read_stats
    
#
    ########### calculate intersection of NDf and TDf ###############

    #returns the filenames of the gff files with the intersection sets of tumor and normal predictions
    # Tn -> in Tumor, not in Normal
    # TN -> in Tumor and Normal
    # tN -> not in Tumor, in Normal

    #f means filtered
 
    ##### calculate the intersection of TDf and NDf ##################
    #(Tf_nf, Tf_Nf, tf_Nf) = venn_diag(t_F_gff, "Tf", n_F_gff, "Nf", library_name, False, plot)


    ##### calculate the intersection of TDf and ND ##################
    t_F_gff = args.tdf
    n_gff = args.nd
    library_name=args.o
    bam_file=args.bam
    
    
    (Tf_n, Tf_N, tf_N) = venn_diag(t_F_gff, "Tf", n_gff, "ND", library_name, True, plot)

     ##### calculate the intersection of TD and ND ##################
    #(T_n, T_N, t_N) = venn_diag(t_gff, "T", n_gff, "N", library_name, False, plot)


    ############## inspect reads at loci of ins predicted in filtered T set, and absent from Normal unfiltered set #################

    # open bam file as a pysam obects, from which to retrieve the reads at each locus
    reads = pysam.Samfile(bam_file, "rb")

    putative_som_ins = open(library_name + ".Tf.not_ND.context_read_stats.gff", "w")
    # putative_som_ins.write("\t".join(["chr", "method", "type", "start", "end", "score", "strand", "phase", "tags", \
                                    # "stats for reads +/- 100 bp of insertion interval: softclipped%", "discordant_total", "discordant%", "proper_total", "proper%", "total_count", "\n"]))
    

    for line in open(Tf_n):

        line = line.strip()
        #ignore empty line or comment lines
        if line[0] == '#':
            continue
        if line == "":
            continue

        feature = GffAnnot(line)

        # try:
        #     feature.tags["softclipped_pos"]
        #     (clip_start, clip_stop) = feature.tags["softclipped_pos"][1:-1].split(", ")
        #     clip_start = int(clip_start)
        #     clip_stop = int(clip_stop)

        # except KeyError:
        #     print feature.toString() + "\t" + "no softclipped tag"
        #     continue

        # if clip_start == -1 or clip_stop == -1 :
        #     print feature.toString() + "\t" + "no softclipped pos"
        #     continue

        #print "############# chr " + feature.chrom + "  #########################"
        reads_iter = reads.fetch(feature.chrom, feature.start - 100, feature.stop + 100)
        # print feature.chrom, feature.start - 100, feature.stop + 100

        (unmapped_count, proper_softclipped_count,  long_discordant_softclipped_count, short_discordant_softclipped_count, long_discordant_count, short_discordant_count, proper_count, unknown_map_count, max_mapq,  min_mapq, avg_mapq, total_count) = get_read_stats(reads_iter, read_stats)
        
        softclipped_total = proper_softclipped_count + long_discordant_softclipped_count + short_discordant_softclipped_count
        softclipped_per = softclipped_total / total_count * 100

        discordant_total = long_discordant_softclipped_count + long_discordant_count
        discordant_per = discordant_total / total_count * 100
        
        proper_total = proper_softclipped_count + proper_count
        proper_per = proper_total / total_count * 100

        read_stats_values = [softclipped_total, softclipped_per, discordant_total, discordant_per, proper_total, proper_per, total_count]
        read_stats_tags = ["softclipped_total", "softclipped_per", "discordant_total", "discordant_per", "proper_total", "proper_per", "total_count"]
        read_stat_tag_line = ";".join([(lambda x,y: "%s=%f" % (x,y))(x,y) for (x,y) in zip(read_stats_tags, read_stats_values)])

        read_stat_line = "\t".join(map(str, read_stats_values))
        

        if discordant_per > 1:
            # putative_som_ins.write(feature.to_string() + "\t" + read_stat_line + "\tNON-SOM\n"
            putative_som_ins.write(feature.to_string() + ";" + read_stat_tag_line + ";call=NON_SOM\n")
        else:
            # putative_som_ins.write(feature.to_string() + "\t" + read_stat_line + "\tPUTATIVE-SOM\n")
            putative_som_ins.write(feature.to_string() + ";" + read_stat_tag_line + ";call=PUTATIVE_SOM\n")





        #print feature.toString() + "\t" + read_stats_str 

    reads.close()






###############################

def get_read_stats(bam_file_iter, read_stats):

    proper_softclipped_count = 0    

    long_discordant_softclipped_count = 0
    short_discordant_softclipped_count = 0

    long_discordant_count = 0
    short_discordant_count = 0

    proper_count = 0

    unmapped_count = 0

    unknown_map_count = 0

    total_count = 0.0

    



    
    try:
        read = bam_file_iter.next()
    except StopIteration:
        # return "%d\t%.2f\t%d\t%.2f\t%d\t%.2f\t%d\t%.2f\t%.2f\t%.2f\t%.2f\t" % (0, 0.0, \
        #                             0, 0.0, \
        #                             0, 0.0, \
        #                             0, 0.0, \
        #                             0,  0, 0.0, 0)       
        return (0, 0.0, \
                0, 0.0, \
                0, 0.0, \
                0, 0.0, \
                0,  0, 0.0, 0)       

    mapq_list = []
    
    verbose = False

    while 1 :
        total_count = total_count + 1
        mapq_list.append(read.mapq)
        
        # if verbose:
        #     print "next pair"

        # if verbose:
        #     print read
           
        # this will be "long", "short" or ""
        read_is_discordant = is_discordant(read, read_stats["fragment_length"], read_stats["fragment_length_SD"])
            
        if read.is_unmapped:
            if verbose:
                print "unmapped!"
                print read
                print "is_unmapped", read.is_unmapped
                print "tlen", read.tlen
                print "pos", read.pos
                print "mate_is_unmapped", read.mate_is_unmapped
                print "pnext", read.pnext

            unmapped_count += 1
            try:
                read = bam_file_iter.next()
                
            except StopIteration:
                break
            
        
        if is_softclipped(read) and read.is_proper_pair:
            if verbose:
                print "proper softclipped map!"
                print read.tlen
            proper_softclipped_count += 1
            try:
                read = bam_file_iter.next()
               
            except StopIteration:
                break
            
        
        elif is_softclipped(read) and read_is_discordant:
            if verbose:
                print "discordant softclipped map!"
                print read.tlen
            if read_is_discordant == "long":
                long_discordant_softclipped_count += 1

            elif read_is_discordant == "short":
                short_discordant_softclipped_count += 1

            try:
                read = bam_file_iter.next()
               
            except StopIteration:
                break
            
        
        elif read.is_proper_pair:
            if verbose:
                print "proper pair!"
                print "tlen", read.tlen
            proper_count +=1
            try:
                read = bam_file_iter.next()
                
            except StopIteration:
                break
            
        

        elif read_is_discordant:
            if verbose:
                print "discordant!"
                print "unmapped", read.is_unmapped
                print "tlen", read.tlen
                print "pos", read.pos
                print "mate_is_unmapped", read.mate_is_unmapped
                print "pnext", read.pnext

            if read_is_discordant == "long":
                long_discordant_count += 1
                if verbose:
                    print "long discordant!"
            elif read_is_discordant == "short":
                short_discordant_count += 1
                if verbose:
                    print "short discordant!"
            
            try:
                read = bam_file_iter.next()
               
            except StopIteration:
                break
        else:
            if verbose:
                print "unknown!"
                print "unmapped", read.is_unmapped
                print "tlen", read.tlen
                print "pos", read.pos
                print "mate_is_unmapped", read.mate_is_unmapped
                print "pnext", read.pnext

            unknown_map_count += 1

            try:
                read = bam_file_iter.next()
           
            except StopIteration:
                break
            
            
        

    # total = proper_softclipped_count + discordant_softclipped_count + discordant_count + proper_count 

    

    return (unmapped_count, \
            proper_softclipped_count,  \
            long_discordant_softclipped_count,  \
            short_discordant_softclipped_count, \
            long_discordant_count,  \
            short_discordant_count, \
            proper_count,  \
            unknown_map_count, \
            max(mapq_list),  min(mapq_list), np.average(mapq_list), total_count)

    # return "%d\t%.2f\t%d\t%.2f\t%d\t%.2f\t%d\t%.2f\t%.2f\t%.2f\t%.2f\t%d" % (proper_softclipped_count, (proper_softclipped_count / total_count ) * 100, \
    #                                     discordant_softclipped_count, (discordant_softclipped_count / total_count ) * 100, \
    #                                     discordant_count, (discordant_count  / total_count ) * 100, \
    #                                     proper_count, (proper_count / total_count ) * 100, \
    #                                     max(mapq_list),  min(mapq_list), np.average(mapq_list), total_count)
    

    
    
def is_mapped_mult_times(read):
    if read.tags != None:
        try:
            if read.opt('XT') == 'R':
                return 1
        except KeyError:
            pass
        try:
            if read.opt('X0') != None:
                if read.opt('X0') > 1:
                    return 1
        except KeyError:
            pass
        try:
            if read.opt('X1') != None:
                if read.opt('X1') > 0:
                    return 1
        except KeyError:
            pass
        return 0
    else:
        return 0


def is_softclipped(read):
    if read.cigar == None:
        return 0
    for op, num in read.cigar:
        if op == 4:
            return 1

    return 0

def is_discordant(read, fragment_length, fragment_length_SD):
    if abs(read.tlen) > fragment_length + 2*fragment_length_SD:
        return "long"
    elif read.tlen == 0:
        return "long"
    elif abs(read.tlen) < fragment_length - 2*fragment_length_SD:
        return "short"
    else:
        return ""


def venn_diag(gff1, label1, gff2, label2, library_name, save, plot):

    outfile_name = library_name + "_" + label1 + "." + label2
    
    figure = plt.figure()

    a = pybed.BedTool(gff1)
    b = pybed.BedTool(gff2)
    
    Ab = (a - b)
    aB = (b - a)
    AB = (a + b)

    

    
    v = venn2(subsets=(Ab.count(), aB.count(), AB.count()), set_labels = (label1, label2))
    # #plt.text(0,0,results)

    Ab_name = "%s_%s.not%s.gff" % (library_name, label1, label2)
    if save:
        Ab.saveas(Ab_name)

    aB_name = "not%s.%s.gff" % (label1, label2)
    # # aB.saveas(aB_name)

    AB_name = "%s.%s.gff" % (label1, label2)
    # # AB.saveas(AB_name)


    # #plt.show()

    # # out_report = open(outfile_name + "_venn_diagram_report.txt" , "w")
    # # results = "%s\t%s\n" % (label1, label2)
    # # results = results + "x\t \t%d\n" % (Ab.count())
    # # results = results + " \tx\t%d\n" % (aB.count())
    # # results = results + "x\tx\t%d\n" % (AB.count())
    # # out_report.write(results)
    # # out_report.close()

    if plot:
        plt.savefig(outfile_name + ".pdf", format='pdf')
    return (Ab_name, AB_name, aB_name)

    
if __name__ == "__main__":
    main(sys.argv[1:])
