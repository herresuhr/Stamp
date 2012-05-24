#!/usr/bin/env python


#	Script name: 	stamp.py
#	Written by:		Troels Suhr Skovgaard
#	Date: 			24.05.2012
#
#	Copies and renames input dir/file and changes a single running variable.
#
#	Written for producing many copies of the same input .cpp file while changing only name #	and variable.



import argparse
import os
import numpy as np
import subprocess

def main():
	
	# Setup basic command line info
	p = argparse.ArgumentParser(description="Copy and rename directory and file "
					   					   +"while running through parameter range.")
										   
	p.add_argument("filein",   type=str, help="File to be stamped.")
	p.add_argument("varname",  type=str, help="Variable name")
	p.add_argument("varrange", type=str, help="Variable range (min:max:NumElem)")
	p.add_argument('--directory', '-d', default='.',
				   			   type=str, help="Directory to be stamped. ")
	
	args = p.parse_args()

	# Separate input filename in name and extension	
	prefile, postfile = args.filein.split('.')
	
	# Construct numpy range from input range
	rangeparts = args.varrange.split(':')
	ran = np.linspace(float(rangeparts[0]),
	                  float(rangeparts[1]),
					  int(rangeparts[2]))
	
	# Handles directory. If no directory is specified, set to pwd
	if(args.directory is '.'):
		
		# PIPE channels possible errors to output
		p = subprocess.Popen(['pwd'],
		      stdout=subprocess.PIPE,
			  stderr=subprocess.PIPE)
		out, err = p.communicate()
		
		# Remove possible line break
		args.directory = '../' + out.split('/')[-1].replace("\n","")
	
	# Step through variable range. For each, construct directory (+log),
	# copy/rename file, replace fn and variable values in file
	for v in ran:
		# Current vars
		curfin  = args.directory + '/' + args.filein
		curdir  = args.directory + '_' + args.varname + str(v)
		curfout = prefile + '_' + args.varname + str(v) + '.' + postfile
		
		# Construct directory tree
		os.system('mkdir -p ' + curdir + '/log')
		
		# Copy and rename
		os.system('cp -i ' + curfin + ' ' + curdir + '/' + curfout)
		
		# Find fn variable in file, split at = and replace value
		p = subprocess.Popen(['grep', 'const string fn', curdir + '/' + curfout],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE)
		out, err = p.communicate()
		
		out = out.replace("\n","") # Remove possible line break		
		fn = out.split('=')[0] + '= "' + prefile + '_' + args.varname + str(v) + '";'
		os.system("perl -p -i -e 's/" + out + "/" + fn + "/g' " + curdir + "/" + curfout)
		
		# Find variable in file, split at = and replace value
		p = subprocess.Popen(['grep', '-w', '-m1', args.varname, curdir + '/' + curfout],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE)
		out, err = p.communicate()
		
		out = out.replace("\n","") # Remove possible line break		
		var = out.split('=')[0] + '= ' + str(v) + ';'
		os.system("perl -p -i -e 's/" + out + "/" + var + "/g' " + curdir + "/" + curfout)

		# Finally, report
		print "created: " + curdir + "/" + curfout

if __name__ == '__main__':
	main()