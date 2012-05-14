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
				basename, extension = os.path.splitext(file)

				f = tagpy.FileRef( file )
				tag = f.tag()

				artist = self.normalise(tag.artist)
				title = self.normalise(tag.title)
				album = self.normalise(tag.album)
				track = tag.track
				filemap[file] = self.createNewName(artist, album, track, title, extension)

				print "%s/%s/%d/%s  -> " % (tag.artist,tag.album,tag.track,tag.title),
				print filemap[file]

		elif self.options.mode == 'testnormalise':
			for teststring in self.positionalparameters:
				print self.normalise( teststring )

	#
	# Function:		createNewName
	# Description:
	#
	def createNewName( self, artist, album, track, title, extension ):
		variableList = [artist]
		formatString = ["%s/"]

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
		newname = re.sub(r'[ \(\),;\.!\?\-_]+', r' ', newname )
		# Contract punctuation
		newname = re.sub(r'\'+', r'', newname )
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
#		parser.add_option( "-d", "--draft", dest="draft",
#			action="store_true", default=self.options.draft,
#			help="upload as draft articles")
#		parser.add_option( "-l", "--login", dest="username",
#			metavar="USERNAME", type='string', default=self.options.username,
#			help="the username of your google account [default:%default]")
#		parser.add_option( "-p", "--password", dest="password",
#			metavar="PASSWORD", type='string', default=self.options.password,
#			help="the password of your google account [default:NOT SHOWN]")
		parser.add_option( "-n", "--tracknums", dest="tracknums",
			action="store_true",
			help="Prefix track names with the track number")
		parser.add_option( "-a", "--albums", dest="includealbum",
			action="store_true",
			help="Include the album name as part of the path")
#		parser.add_option( "", "--listblogs", dest="mode",
#			action="store_const", const="listblogs",
#			help="List the available blogs")
#		parser.add_option( "", "--testmd", dest="mode",
#			action="store_const", const="testmd",
#			help="Test the ikiwiki-to-markdown engine from the supplied filenames")
#		parser.add_option( "", "--sync", dest="mode",
#			action="store_const", const="sync",
#			help="Use article titles to look up post IDs")
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

