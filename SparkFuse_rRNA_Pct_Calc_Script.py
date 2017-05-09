# @file rrna_pct_calc.py
#
# Calculates the number of rRNA reads, and the percent of
# reads that the rRNA reads make up for.
#
# Required inputs:
# -i/--input 	The BAM file to process.
# -b/--bed 		A BED file containing the rRNA region coordinates.
# --samtools 	The filepath to the SAMtools executable (e.g. /path/to/bin/samtools).
# --bedtools 	The filepath to the bedtools executable (e.g. /path/to/bin/bedtools)

import sys
import os
import argparse
import subprocess

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='rRNA Percent Calculation')
	parser.add_argument('-i', '--input', help='Input file')
	parser.add_argument('-b', '--bed', help='BED file')
	parser.add_argument('-o', '--output', help='Output file')
	parser.add_argument('--samtools', help='Path to samtools')
	parser.add_argument('--bedtools', help='Path to bedtools')
	args = parser.parse_args(sys.argv[1:])


	if args.input is None:
		print('Error: Input file not specified.')
		exit()
	else:
		input_bam = os.path.abspath(args.input)
		if os.path.isfile(input_bam) is False:
			print('Error: Input file {0} does not exist.'.format(input_bam))
			exit()


	if args.bed is None:
		print('Error: BED file not specified.')
		exit()
	else:
		bed_file_path = os.path.abspath(args.bed)
		if os.path.isfile(bed_file_path) is False:
			print('Error: BED file {0} does not exist.'.format(bed_file_path))
			exit()


	if args.output is None:
		print('Error: Output file not specified.')
		exit()
	else:
		output_filepath = os.path.abspath(args.output)


	if args.samtools is None:
		print('Error: Path to samtools not specified.')
		exit()
	else:
		samtools_path = os.path.abspath(args.samtools)
		if os.path.isfile(samtools_path) is False:
			print('Error: samtools not found at {0}'.format(samtools_path))
			exit()


	if args.bedtools is None:
		print('Error: Path to bedtools not specified.')
		exit()
	else:
		bedtools_path = os.path.abspath(args.bedtools)
		if os.path.isfile(bedtools_path) is False:
			print('Error: bedtools not found at {0}'.format(bedtools_path))
			exit()


	# Generate filenames for the intermediate files.
	name_sorted_prefix = os.path.basename(input_bam).replace('.bam', '.name_sorted')
	name_sorted_prefix = input_bam.replace(os.path.basename(input_bam), name_sorted_prefix)
	name_sorted_bam = name_sorted_prefix + '.bam'
	name_sorted_intx = name_sorted_prefix + '.intx'

	# Sort by name for bedtools
	os.system('{0} sort -n {1} {2}'.format(samtools_path, input_bam, name_sorted_prefix))

	# BEDTools intersect BAM with rRNA.bed
	os.system('{0} pairtobed -abam {1} -b {2} > {3}'.format(bedtools_path, name_sorted_bam, 
		bed_file_path, name_sorted_intx))


	# Get total read count using samtools flagstat
	command = '{0} flagstat {1}'.format(samtools_path, input_bam)
	response = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True).communicate()[0].split('\t')
	
	# Total read count is the first word of the first line of the response
	read_count = int(response[0].strip().split(' ')[0])

	# Get rRNA read count using samtools flagstat
	command = '{0} flagstat {1}'.format(samtools_path, name_sorted_intx)
	response = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True).communicate()[0].split('\t')
	
	# Total read count is the first word of the first line of the response
	rrna_reads = int(response[0].strip().split(' ')[0])


	# Delete temporary files
	os.remove(name_sorted_bam)
	os.remove(name_sorted_intx)

	# Write to output file
	output = open(output_filepath, 'w')
	output.write('RRNA_READS\t{0}'.format(rrna_reads) + '\n')
	output.write('RRNA_PERCENT\t{0}'.format((100.0 * rrna_reads) / read_count) + '\n')
	output.close()
