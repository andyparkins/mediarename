#!/usr/bin/python
# ----------------------------------------------------------------------------
# Project: mediarename
#
# Version Control
#    $Author$
#      $Date$
#        $Id$
#
# Legal
#    Copyright 2010  Andy Parkins
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Notes
#   apt-get install python-tagpy
#
# ----------------------------------------------------------------------------

# ----- Includes

# Standard library
import sys
import os
import shutil
import subprocess
import locale
import time
import re
import codecs
from optparse import OptionParser

# Additional
from xml.dom import minidom
import tagpy


# ----- Constants


# ----- Class definitions

#
# Class:
# Description:
#
class Record:
	pass

#
# Class:
# Description:
#
class TMediaRenameError(Exception):
	pass

#
# Class:	TMediaRename
# Description:
#
class TMediaRename:
	#
	# Function:		__init__
	# Description:
	#
	def __init__( self, argv ):
		self.argv = argv

		# Load the options record with default values
		self.options = Record()
		self.options.tracknums = False
		self.options.includealbum = False
		self.options.pathprefix = ''
		self.options.mode = 'default-mode'

	#
	# Function:		run
	# Description:
	#
	def run( self ):
		self.readCommandLine()

		if self.options.verbose:
			print >> sys.stderr,  "mediarename: --- Verbose mode active"
			print >> sys.stderr,  self

		if self.options.mode == 'default-mode':
			print >> sys.stderr, "mediarename: --- Command line mode"

			filemap = dict()
			for file in self.positionalparameters:
				filemap[file] = self.processFile(file)
				if filemap[file] is None:
					continue

				if self.options.verbose:
					print filemap[file]

				try:
					self.renameWithPathCreate( file, filemap[file] )
				except Exception, e:
					print >> sys.stderr,  "mediarename: ERROR creating target:",e.args[0]
					raise

		elif self.options.mode == 'testnormalise':
			for teststring in self.positionalparameters:
				print self.normalise( teststring )

	#
	# Function:		renameWithPathCreate
	# Description:
	#
	def renameWithPathCreate( self, fromfile, tofile ):
		newdirname = os.path.dirname( tofile )

		if not os.path.exists( newdirname ):
			if self.options.verbose or self.options.dryrun:
				print "mediarename: Creating directory '%s'" % (newdirname)
			if not self.options.dryrun:
				os.makedirs( newdirname )

		if os.path.exists( tofile ):
			print "mediarename: skipping existing target,", tofile
			return

		print "mediarename: '%s' => '%s'" % (fromfile, tofile)
		if not self.options.dryrun:
			shutil.copy2( fromfile, tofile )

	#
	# Function:		processFile
	# Description:
	#
	def processFile( self, file, n = None ):
		if not os.path.exists( file ):
			print >> sys.stderr, "mediarename: skipping non-existent file", file
			return None

		basename, extension = os.path.splitext(file)

		try:
			f = tagpy.FileRef( file )
			tag = f.tag()
		except ValueError, e:
			print >> sys.stderr, "mediarename: skipping unsupported file type", file
			return None

		artist = self.normalise(tag.artist)
		title = self.normalise(tag.title)
		album = self.normalise(tag.album)
		track = tag.track
		if track is None and n is not None:
			track = n
		newname = self.createNewName(artist, album, track, title, extension)

		if self.options.verbose:
			print "%s/%s/%d/%s  -> " % (tag.artist,tag.album,tag.track,tag.title),

		return newname

	#
	# Function:		createNewName
	# Description:
	#
	def createNewName( self, artist, album, track, title, extension ):
		formatString = []
		variableList = []

		if self.options.pathprefix:
			variableList.append( self.options.pathprefix )
			formatString.append( "%s/" )

		variableList.append( artist )
		formatString.append( "%s/" )

		if self.options.includealbum:
			variableList.append(album)
			formatString.append("%s/")

		if self.options.tracknums:
			variableList.append(track)
			formatString.append("%03.3d_")

		variableList.append(title)
		formatString.append("%s")
		variableList.append(extension)
		formatString.append("%s")

		return ''.join(formatString) % tuple( variableList )


	#
	# Function:		normalise
	# Description:
	#
	def normalise( self, name ):
#		newname = re.sub(r'\[(.+?)\]: *<(.+)>', r'[\1]: \2', newname )
	
		newname = name
		# Separators to spaces
		newname = re.sub(r'[ \(\),;:|\.!\?\-_\\\/]+', r' ', newname )
		# Contract punctuation
		newname = re.sub(r'[\'"]+', r'', newname )
		# Ampersand
		newname = re.sub(r'&', r'And', newname )

		# Titlecase
		newname = newname.title()

		# Move "the" to the end
		newname = re.sub(r'^The (.+)', r'\1The', newname )

		# Strip remaining spaces
		newname = re.sub(r' ', r'', newname )

		return newname


	#
	# Function:		readCommandLine
	# Description:
	#  Parse the command line with OptionParser; which supplies all the
	#  niceties for us (like --help, --version and validating the inputs)
	#
	def readCommandLine( self ):
		# Configure parser
		parser = OptionParser(
			usage="usage: %prog [options]",
			version="%prog 1.0")
		# "-h", "--help" supplied automatically by OptionParser
		parser.add_option( "-v", "--verbose", dest="verbose",
			action="store_true",
			help="show verbose output")
		parser.add_option( "-p", "--path", dest="pathprefix",
			metavar="PATH", type='string', default=self.options.pathprefix,
			help="use PATH rather than the current directory as target")
		parser.add_option( "-n", "--tracknums", dest="tracknums",
			action="store_true",
			help="Prefix track names with the track number")
		parser.add_option( "-a", "--albums", dest="includealbum",
			action="store_true",
			help="Include the album name as part of the path")
		parser.add_option( "-d", "--dry-run", dest="dryrun",
			action="store_true",
			help="Don't actually change anything, implies verbose")
		parser.add_option( "", "--test", dest="mode",
			action="store_const", const="testnormalise",
			help="Test the normalisation patterns")
		parser.set_defaults(mode=self.options.mode, \
			tracknums=self.options.tracknums, \
			includealbum=self.options.includealbum
			)

		# Run the parser
		(self.options, args) = parser.parse_args( self.argv[1:] )

		# Copy the positional arguments into self
		self.positionalparameters = args


	#
	# Function:		__str__
	# Description:
	#  Dump the contents of this class to a string
	#
	def __str__( self ) :
		s = repr(self) + "\n";
		for var in self.__dict__ :
			s = s + " - " + var + " = " + str(self.__dict__[var]) + "\n"
		return s


# ----- Main
#
# Function:		main
# Description:
#
def main( argv = None ):
	# Default arguments from command line
	if argv is None:
		argv = sys.argv

	# Locale
	locale.setlocale( locale.LC_ALL, '' );

	app = TMediaRename( argv )

	# --- Begin
	try:
		app.run()

	# Simply display TMediaRenameErrors
	except TMediaRenameError, e:
		print >> sys.stderr,  "mediarename: ERROR:",e.args[0]


# ----- Module check
#
# __name__ is set to "__main__" when this is the top module
# if this module is loaded because of an "import" then this
# won't get run -- perfect
if __name__ == "__main__":
	sys.exit( main() )

