#!/usr/bin/env python

# StepMania Unlock Code Generator - Utility for locking song in StepMania
# Copyright (C) 2008 Travis Nickles <ryoohki7@yahoo.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import pygtk
if not sys.platform == 'win32':
	pygtk.require ("2.0")
import gtk
import gtk.glade
from time import time
from shutil import copy
import getopt
from threading import Thread
import webbrowser

# For debugging purposes only.
# Comment out for any public release
import gc
gc.set_debug (gc.DEBUG_LEAK)

# Version number of application
VERSION_NUMBER = "0.6"

# Set application name
APP_NAME = "StepMania Unlock Code Generator"

# Holds the memory address of all the SongGroup objects created
group_collection = []


class SongGroup:
	changes = []
	def __init__ (self, name, songs=[]):
		self.name = name.decode ('utf8', 'replace')
		self.songs = songs
		self.values = [0, 0, 0, 0, 0]
		self._defaults = [0, 0, 0, 0, 0]

	def reset (self):
		self.values = self._defaults
		for song in self.songs:
			song.reset ()

	# A SongGroup object values have been changed. Update the values of all the songs
	# listed in the SongGroup
	def change_songs (self):
		for song in self.songs:
			song.arcade, song.clear, song.dance, song.roulette, song.song = self.values

class Song:
	def __init__ (self, name, name_trans, arcade=0, clear=0, dance=0, roulette=0, song=0):
#		print name
		self.name = name.decode ('utf8', 'replace')
		self.name_trans = name_trans.decode ('utf8', 'replace')
		self.arcade = arcade
		self.clear = clear
		self.dance = dance
		self.roulette = roulette
		self.song = song
		self._defaults = [arcade, clear, dance, roulette, song]

	def reset (self):
		self.arcade, self.clear, self.dance, self.roulette, self.song = self._defaults

	# An unlock code has been found for this song. Update the values and defaults for this
	# Song object according to the unlock code values
	def unlock_values (self, changes):
		self._defaults = changes
		self.arcade, self.clear, self.dance, self.roulette, self.song = self._defaults


class StepManiaLocker:
	# Starts the search process and updates the interface when the
	# dirty work has been completed
	def load_smfiles (self, skip=False):
		# Create a blank group and append it to group_collection. Will later
		# hold a sorted (by name) list containing the memory address of
		# every song object
		starttime = time ()
		newgroup = SongGroup ("<b>All</b>")
		group_collection.append (newgroup)

		# If the Songs folder has been selected, make searchfolder the directory
		# above the Songs directory
		if os.path.basename (self.searchfolder) == "Songs":
			self.searchfolder = os.path.dirname (self.searchfolder)

		# Start searching for songs, organize the songs,  and attempt
		# to read the Unlocks.dat file
		startwalk = time ()
		filewalk (self.searchfolder, self.statusbar, self.statusbar_context_id)
		# If no songs have been loaded, print error text, display a warning window, and exit the program
		if len (group_collection) <= 1:
			print >> sys.stderr, "Directory \"%s\" is either invalid or contains no song files. Exiting." % self.searchfolder
			if skip:
				self.skip = True
			gtk.gdk.threads_enter ()
			self.dir_warning_text.set_text ("Directory %s\nis either invalid or contains no song files. Exiting." % self.searchfolder)
			self.invalid_dir_window.run ()
			gtk.gdk.threads_leave ()
			return
		endtime = time ()
		print "FileWalk func:        %.3f" % (endtime - startwalk)

		# Fill first group with all songs
		for group in group_collection:
			for song in group.songs:
				group_collection[0].songs.append (song)
		group = group_collection[0]
		group.songs.sort (key=lambda x: x.name.lower ())

		print "Files read:           %i" % len (group.songs)
		startunlock = time ()
		status = read_unlock_file (self.searchfolder)
		endtime = time ()
		if status:
			print "Read Unlocks.dat:     %.3f" % (endtime - startunlock)
		print "Total time:           %.3f" % (endtime - starttime)

		# Change interface
		gtk.gdk.threads_enter ()
		self.hbox1.hide ()
		self.hbox2.hide ()
		self.hbox3.hide ()
		self.hbox6.show ()
		self.grouplist.clear ()
		self.songlist.clear ()
		for group in group_collection:
			self.grouplist.append ([group.name])
		for song in group_collection[0].songs:
			self.songlist.append ([song.name])
		self.active_display = True
		self.previous_song_selection = [0, -1]
		tree = self.groupview_selection
		tree.select_path (0)
		self.song_group_label.set_text ("Group Name")
		self.song_name_entry.set_text ("All")
		self.close_menu_option.set_sensitive (True)
		self.songview_selection.set_select_function (self.song_search, None, True)
		gtk.gdk.threads_leave ()
		self.thread = None
		return True

	# Writes the unlock file and shows a prompt telling the user
	# where the unlock file is located
	def write_unlock_file(self, widget):
		# Check if the last selected object has changed and update
		# the object if it has
		group, song = self.previous_song_selection
		self.spinbuttons_update ()
		if group >= 0 and song == -1:
			changed = self.get_group_spinbutton_values (group_collection[group])
			if changed:
				group_edit = group_collection[group]
				group_edit.change_songs ()
		else:
			previous_song = group_collection[group].songs[song]
			self.get_song_spinbutton_values (previous_song)

		# Attempt to make a backup copy of the Unlocks.dat file
		datafolder = os.path.join (self.searchfolder, "Data")
		if (os.path.isdir (datafolder)):
			writefile = os.path.join (datafolder, "Unlocks.dat")
			if (os.path.isfile (writefile)):
				backupfile = os.path.join (datafolder, "Unlocks.dat.backup")
				try:
					copy (writefile, backupfile)
					print "Backup File: %s" % backupfile
				except (IOError, OSError):
					print >> sys.stderr, "Permission denied for writing to %s." % backupfile
					print >> sys.stderr, "No backup file will be created."
		else:
			home = os.path.expanduser ("~")
			writefile = os.path.join (home, "Unlocks.dat")
			if (os.path.isfile (writefile)):
				backupfile = os.path.join (home, "Unlocks.dat.backup")
				try:
					copy (writefile, backupfile)
					print "Backup File: %s" % backupfile
				except (IOError, OSError):
					print >> sys.stderr, "Permission denied for writing to %s." % backupfile
					print >> sys.stderr, "No backup file will be created."

		# Starts the writing of the Unlocks.dat file
		message = """// Test file for Miryo's new Unlock system.\n\
// Songs/courses are matched by name, not folder name\n\
//\n\
// System modified by curewater\n\
//\n\
// The following methods are implemented:\n\
//\n\
// DP - Dance points, e.g. 2 per perfect, 1 per great, etc.\n\
// AP - Arcade points, like MAX2 arcade\n\
// SP - Song points, like MAX2 Home\n\
// CS - Clear Stages, like 5th Home\n\
// RO - Roulette, unlocked by landing on it in roulette.\n\
//\n\
// To be implemented: Toasty, Clear Extra Stages, Fail Extra Stages.\n\
//\n\
// Courses will be implemented eventually, but not yet.\n\
// Songs are matched by title + subtitle.\n\
//\n\
// Any line not starting with #UNLOCK will be ignored.\n\
//\n\
// Sample lines:\n\
//\n\
// #UNLOCK:xenon:AP=10;\n\
// Song xenon requires 10 arcade points to unlock.\n\
//\n\
// #UNLOCK:the Legend of MAX:RO=3\n\
// Song "the Legend of Max" is in roulette slot 3.\n\
//\n\
// #UNLOCK:PARANOIA SURVIVOR MAX:CS=30,RO=3;\n\
// Song "Paranoia Surivvor MAX" is locked either by clearing\n\
// 30 stages, or by landing on it in roulette slot 3.\n\
//\n\
// #UNLOCK:POP 4:CS=50;\n\
// Course Pop 4 is locked until 50 stages are cleared.\n\
// (Stepmania doesn't distinguish between song and course titles\n\
// yet.\n\
//\n\n"""
		starttime = time ()
		try:
			file = open (writefile, 'w')
		except IOError:
			print >> sys.stderr, "Permission denied for writing to %s. Exiting program." % writefile
			self.prompt_text.set_text ("Permission denied for writing to\n%s. Exiting program." % writefile)
			self.prompt_window.run ()
			return

		file.write(message)
		group = group_collection[0]
		for song in group.songs:
#			print song
			i = 1
			changes = []
			# Find which properties have been changed
			# and place the categories in a temporary list
			for stat in [song.arcade, song.clear, song.dance, song.roulette, song.song]:
				if stat != 0:
					if i == 1:
						changes.append ("arcade")
					elif i == 2:
						changes.append ("clear")
					elif i == 3:
						changes.append ("dance")
					elif i == 4:
						changes.append ("roulette")
					else:
						changes.append ("song")
				i += 1
			# If any categories exist in the list, write an unlock entry
			# with the categories in the appropriate order
			if changes:
				i = 1
				file.write ("#UNLOCK:%s:" % song.name_trans)
				for stat_type in changes:
					if stat_type == "arcade":
						file.write ("AP=%s" % song.arcade)
					elif stat_type == "clear":
						file.write ("CS=%s" % song.clear)
					elif stat_type == "dance":
						file.write ("DP=%s" % song.dance)
					elif stat_type == "roulette":
						file.write ("RO=%s" % song.roulette)
					elif stat_type == "song":
						file.write ("SP=%s" % song.song)
					if i < len (changes):
						file.write (",")
						i += 1
					else:
						file.write (";\n")
		file.write ('\n')
		file.close ()
		endtime = time ()
		print "Wrote Unlocks.dat:    %.3f" % (endtime - starttime)
		print "Unlock File: %s" % writefile
		# Set text for final prompt window and show the window
		self.prompt_text.set_text ("File Unlocks.dat has been written to\n%s" % writefile)
		self.prompt_window.show ()

	# Changes a SongGroup or Song object, depending, when a new group is selected
	def group_select (self, widget):
		if not self.active_display:
			return
		tree = widget.get_selection()
		model, selection = tree.get_selected ()
		path = model.get_path (selection)

		# The group has been re-selected
		if self.previous_song_selection == [path[0], -1]:
			return

		group, song = self.previous_song_selection
		self.spinbuttons_update ()
		# Change from group to group
		if group >= 0 and song == -1:
			changed = self.get_group_spinbutton_values (group_collection[group])
			if changed:
				group_edit = group_collection[group]
				if not group_edit in group_edit.changes:
					group_edit.changes.append (group_edit)
				group_edit.change_songs ()
		# Change from song to group
		else:
			previous_song = group_collection[group].songs[song]
			changed = self.get_song_spinbutton_values (previous_song)
			if changed:
				group_edit = group_collection[group]
				if not previous_song in group_edit.changes:
					group_edit.changes.append (previous_song)
			tree = self.songview_selection
			tree.unselect_path (song)

		# Make the group selected and change the interface accordingly
		temp_group = path[0]
		current_group = group_collection[temp_group]
		if group != temp_group:
			self.songlist.clear ()
			for song in current_group.songs:
				self.songlist.append ([song.name])
		self.song_group_label.set_text ("Group Name")
		if temp_group == 0:
			self.song_name_entry.set_text ("All")
		else:
			self.song_name_entry.set_text (current_group.name)
		self.set_group_spinbutton_values (current_group)
		self.previous_song_selection = [temp_group, -1]

	# Function is ran once when the song column is first selected, twice if a search
	# has been made, and three times when a new song has been selected.
	# Change the Song and/or SongGroup object accordingly.
	def song_search (self, selection, model, path, is_selected, data):
		# Previous selected song. Ignore and return
		if is_selected:
			return True
		group, song = self.previous_song_selection
		# The current song has already been read. Ignore and return
		if self.previous_song_selection == [group, path[0]]:
			return True
		self.spinbuttons_update ()
		# Change from group to song
		if group >= 0 and song == -1:
			previous_group = group_collection[group]
			changed = self.get_group_spinbutton_values (previous_group)
			if changed:
				group_edit = group_collection[group]
				if not group_edit in group_edit.changes:
					group_edit.changes.append (group_edit)
				group_edit.change_songs ()
		# Change from song to song
		else:
			previous_song = group_collection[group].songs[song]
			changed = self.get_song_spinbutton_values (previous_song)
			if changed:
				temp_group = group_collection[0]
				if not previous_song in temp_group.changes:
					temp_group.changes.append (previous_song)

		# Make the song selected and change the interface accordingly
		temp_song = path[0]
		current_song = group_collection[group].songs[temp_song]
		self.set_song_spinbutton_values (current_song)
		self.song_group_label.set_text ("Song Name")
		self.previous_song_selection = [group, temp_song]
		return True

	# Get each spinbutton value as an integer and place the results
	# in the corresponding entry for the song
	def get_song_spinbutton_values (self, current_song):
		arcade = self.arcade_spinbutton.get_value_as_int ()
		clear = self.clear_spinbutton.get_value_as_int ()
		dance = self.dance_spinbutton.get_value_as_int ()
		roulette = self.roulette_spinbutton.get_value_as_int ()
		song = self.song_spinbutton.get_value_as_int ()
		update = False

		if current_song.arcade != arcade or current_song.clear != clear or \
		current_song.dance != dance or current_song.roulette != roulette or \
		current_song.song != song:
			current_song.arcade = arcade
			current_song.clear = clear
			current_song.dance = dance
			current_song.roulette = roulette
			current_song.song = song
			update = True
		return update

	# Get each spinbutton value as an integer and place the results
	# in the corresponding entry for the group
	def get_group_spinbutton_values (self, current_group):
		arcade = self.arcade_spinbutton.get_value_as_int ()
		clear = self.clear_spinbutton.get_value_as_int ()
		dance = self.dance_spinbutton.get_value_as_int ()
		roulette = self.roulette_spinbutton.get_value_as_int ()
		song = self.song_spinbutton.get_value_as_int ()
		update = False

		if current_group.values[0] != arcade or current_group.values[1] != clear or \
		current_group.values[2] != dance or current_group.values[3] != roulette or \
		current_group.values[4] != song:
			current_group.values = [arcade, clear, dance, roulette, song]
			update = True
		return update

	# Set the spinbuttons and song title entry to correspond
	# to the newly selected song
	def set_song_spinbutton_values (self, current_song):
		self.song_name_entry.set_text (current_song.name)
		self.arcade_spinbutton.set_value (current_song.arcade)
		self.clear_spinbutton.set_value (current_song.clear)
		self.dance_spinbutton.set_value (current_song.dance)
		self.roulette_spinbutton.set_value (current_song.roulette)
		self.song_spinbutton.set_value (current_song.song)

	# Set the spinbuttons and song title entry to correspond
	# to the newly selected group
	def set_group_spinbutton_values (self, current_group):
		self.arcade_spinbutton.set_value (current_group.values[0])
		self.clear_spinbutton.set_value (current_group.values[1])
		self.dance_spinbutton.set_value (current_group.values[2])
		self.roulette_spinbutton.set_value (current_group.values[3])
		self.song_spinbutton.set_value (current_group.values[4])

	# Update all spinbuttons
	def spinbuttons_update (self):
		self.arcade_spinbutton.update ()
		self.clear_spinbutton.update ()
		self.dance_spinbutton.update ()
		self.roulette_spinbutton.update ()
		self.song_spinbutton.update ()

	# If the user has selected a different folder, change the searchfolder variable
	def load_folder (self, widget):
		# If the path has changed, change searchfolder
		if widget.get_filename () != self.searchfolder:
			self.searchfolder = widget.get_filename ()

	# Shows the AboutWindow
	def show_about_window (self, widget):
		self.about_window.show ()

	# Hides the AboutWindow
	def hide_about_window (self, widget, data):
		self.about_window.hide ()

	# Quits the program
	def close_program (self, widget, data=None):
		if self.skip:
			sys.exit (42)
		else:
			gtk.main_quit ()

	# Restore the default settings for songs and groups
	def restore_defaults (self, widget):
		group = group_collection[0]
#		print group.changes
		for change in group.changes:
			change.reset ()
		group.changes = []
		tree = self.groupview_selection
		tree.select_path (0)
		self.songlist.clear ()
		for song in group.songs:
			self.songlist.append ([song.name])
		self.song_group_label.set_text ("Group Name")
		self.song_name_entry.set_text ("All")
		self.set_group_spinbutton_values (group)
		self.previous_song_selection = [0, -1]

	def open_site (self, widget, url):
		webbrowser.open (url)

	def start_load_thread (self, widget, skip=False):
		widget.set_sensitive (False)
		self.folder_chooser.set_sensitive (False)
		self.close_menu_option.set_sensitive (False)
		gtk.main_iteration ()
		self.thread = Thread (target=self.load_smfiles, args=(skip,))
		self.thread.setDaemon (True)
		self.thread.start ()

	def show_preferences_window (self, widget):
		self.pref_window.window.show ()

	def __init__ (self, directory):
		# Grab the current working directory
		maindirname = os.path.dirname (__file__)
		path = os.path.abspath (maindirname)
		self.gladefile = "step-unlock-code-gen.glade"
		gtk.about_dialog_set_url_hook (self.open_site)
		self.window = gtk.glade.XML (os.path.join(path, self.gladefile))
		self.main_window = self.window.get_widget ("MainWindow")
		self.about_window = self.window.get_widget ("AboutWindow")
		self.about_window.set_comments ('Version %s' % VERSION_NUMBER)
		self.about_window.set_name (APP_NAME)
		self.about_window.set_position (gtk.WIN_POS_CENTER)
		self.prompt_window = self.window.get_widget ("PromptWindow")
		self.invalid_dir_window = self.window.get_widget ("InvalidDirWindow")
		self.folder_chooser = self.window.get_widget ("directory_chooser")
		# If a directory is specified, check that the directory exists and
		# set the searchfolder to that directory. Else, use the current
		# working directory
		if directory:
			if os.path.isdir (directory):
				self.searchfolder = directory
			else:
				self.searchfolder = os.getcwd ()
		# Windows only: detect whether the default StepMania root directory
		# exists and use it as the default search directory if it does.
		# Else, use the current working directory
		elif sys.platform == 'win32':
			self.searchfolder = "C:\Program Files\StepMania"
			if not os.path.isdir (self.searchfolder):
				self.searchfolder = os.getcwd ()
		# Else, use the current working directory
		else:
			self.searchfolder = os.getcwd ()
		self.folder_chooser.set_current_folder (self.searchfolder)
		self.load_button = self.window.get_widget ("load_button")
		self.song_name_entry = self.window.get_widget ("song_name_entry")
		self.arcade_spinbutton = self.window.get_widget ("arcade_spinbutton")
		self.clear_spinbutton = self.window.get_widget ("clear_spinbutton")
		self.dance_spinbutton = self.window.get_widget ("dance_spinbutton")
		self.roulette_spinbutton = self.window.get_widget ("roulette_spinbutton")
		self.song_spinbutton = self.window.get_widget ("song_spinbutton")
		self.statusbar = self.window.get_widget ("statusbar1")
		self.statusbar_context_id = self.statusbar.get_context_id ("Statusbar")
		self.hbox1 = self.window.get_widget ("hbox1")
		self.hbox2 = self.window.get_widget ("hbox2")
		self.hbox3 = self.window.get_widget ("hbox3")
		self.hbox6 = self.window.get_widget ("hbox6")
		self.hbox8 = self.window.get_widget ("hbox8")
		self.cancel_button = self.window.get_widget ("cancel_button")
		self.reset_button = self.window.get_widget ("reset_button")
		self.save_button = self.window.get_widget ("save_button")
		self.close_button2 = self.window.get_widget ("close_button2")
		self.prompt_text = self.window.get_widget ("prompt_text")
		self.close_button3 = self.window.get_widget ("close_button3")
		self.dir_warning_text = self.window.get_widget ("dir_warning_text")
		self.groupview = self.window.get_widget ("group_list")
		self.songview = self.window.get_widget ("song_list")
		self.column1 = gtk.TreeViewColumn ("Groups", gtk.CellRendererText(), markup=0)
		self.groupview.append_column (self.column1)
		self.grouplist = gtk.ListStore (str)
		self.groupview.set_model (self.grouplist)
		self.grouplist.append (["<b>All</b>"])
		self.column2 = gtk.TreeViewColumn ("Songs", gtk.CellRendererText(), text=0)
		self.songview.append_column (self.column2)
		self.songlist = gtk.ListStore (str)
		self.songview.set_model (self.songlist)
		self.groupview_selection = self.groupview.get_selection ()
		self.songview_selection = self.songview.get_selection ()
		self.song_group_label = self.window.get_widget ("song_group_label")
		self.close_menu_option = self.window.get_widget ("menu_quit")
		self.active_display = False
		self.skip = False
		self.thread = None
		self.previous_song_selection = [-1, -1]
		dic = { "on_MainWindow_destroy" : gtk.main_quit, 'on_cancel_button_clicked': self.close_program,
		"on_load_button_clicked" : self.start_load_thread,
		"on_group_list_cursor_changed" : self.group_select,
		"on_reset_button_clicked" : self.restore_defaults, "on_save_button_clicked" : self.write_unlock_file,
		"on_directory_chooser_current_folder_changed" : self.load_folder, "on_about_button_clicked" : self.show_about_window,
		"on_AboutWindow_response" : self.hide_about_window, "on_close_button2_clicked" : self.close_program,
		"on_PromptWindow_response" : self.close_program, "on_close_button3_clicked" : self.close_program,
		"on_InvalidDirWindow_response" : self.close_program, "on_menu_quit_activate": self.close_program,
		"on_menu_about_activate": self.show_about_window }
		self.window.signal_autoconnect (dic)

# Directory search that finds all the .sm/.dwi files, passes the files found for
# each group to smfile_read, makes all the required SongGroup objects,
# and updates the statusbar
def filewalk (searchfolder, statusbar, context_id):
	searchfolder = os.path.join (searchfolder, "Songs")
	if not os.path.isdir (searchfolder):
		return
	root = os.listdir (searchfolder)
	root.sort (key=lambda x: x.lower())
	for folders in root:
		group_folder = os.path.join (searchfolder, folders)
		if os.path.isdir (group_folder):
			song_folders = os.listdir (group_folder)
			songpaths = []
			for song_folder in song_folders:
				if os.path.isdir (os.path.join(group_folder, song_folder)):
					song_files = os.listdir (os.path.join(group_folder, song_folder))
					song_files.sort (key=lambda x: x.lower())
					song_files.reverse ()
					for song_file in song_files:
						if song_file[-3:].lower () == ".sm":
							filepath = os.path.join (group_folder, song_folder, song_file)
							songpaths.append (filepath)
#							print "Sm:  " + file
							break
						if song_file[-4:].lower () == ".dwi":
							filepath = os.path.join (group_folder, song_folder, song_file)
							songpaths.append (filepath)
#							print "Dwi: " + file
							break

			if len (songpaths) == 0:
				continue
			gtk.gdk.threads_enter ()
			statusbar.pop (context_id)
			statusbar.push (context_id, "Loading Group: %s" % folders)
			gtk.gdk.threads_leave ()

			entries = smfile_read (songpaths)
			if len (entries) == 0:
				continue
			entries.sort (key=lambda x: x.name.lower ())
			newgroup = SongGroup (folders, entries)
			group_collection.append (newgroup)

	gtk.gdk.threads_enter ()
	statusbar.pop (context_id)
	gtk.gdk.threads_leave ()

# Reads in the .sm/.dwi files within a group folder, makes the
# required Song objects, and returns the list of Song objects
def smfile_read (songfiles):
	entries = []
	for filepath in songfiles:
		# Double check to make sure the file exists prior to reading it.
		# Especially necessary when trying to read files with Unicode names
		# under Windows
		if not os.path.exists (filepath):
			print >> sys.stderr, "%s could not be read. Skipping." % filepath
			continue

		temp_filepath = filepath.lower ()
		if temp_filepath[-4:] == ".dwi":
			filetype = ".dwi"
		else:
			filetype = ".sm"
		title = ""
		subtitle = ""
		title_trans = ""
		subtitle_trans = ""

		try:
			file = open (filepath, 'r')
		except IOError:
			print >> sys.stderr, "%s could not be read. Skipping." % filepath
			continue
		readline = file.readline ()
		while readline:
			if filetype == ".dwi" and title:
				break
			elif filetype == ".sm" and title and subtitle and title_trans and subtitle_trans:
				break

			if readline.find ("#TITLE:") != -1:
				c, parsedline = readline.strip().split("#TITLE:")
				parsedline = parsedline.rstrip (';')
				if filetype == ".dwi":
					title = ' '.join (parsedline.split())
				else:
					title = parsedline.strip ()
			elif filetype != ".sm":
				readline = file.readline ()
				continue
			elif readline.find ("#SUBTITLE:") != -1:
				c, parsedline = readline.strip().split("#SUBTITLE:")
				parsedline = parsedline.rstrip (';')
				subtitle = parsedline.strip ()
			elif readline.find ("#TITLETRANSLIT:") != -1:
				c, parsedline = readline.strip().split("#TITLETRANSLIT:")
				parsedline = parsedline.rstrip (';')
				title_trans = parsedline.strip ()
			elif readline.find ("#SUBTITLETRANSLIT:") != -1:
				c, parsedline = readline.strip().split("#SUBTITLETRANSLIT:")
				parsedline = parsedline.rstrip (';')
				subtitle_trans = parsedline.strip ()
			readline = file.readline ()
		file.close ()

		if not title:
			continue
		if not title_trans:
			title_trans = title
		if not subtitle_trans:
			subtitle_trans = subtitle

		if not subtitle and not subtitle_trans:
			temp_song = Song (title, title_trans)
		elif not subtitle:
			temp_song = Song (title, "%s %s" % (title_trans, subtitle_trans))
		elif not subtitle_trans:
			temp_song = Song ("%s %s" % (title, subtitle), title_trans)
		else:
			temp_song = Song ("%s %s" % (title, subtitle), "%s %s" % (title_trans, subtitle_trans))
		entries.append (temp_song)
	return entries

# Reads the unlock codes from the Unlocks.dat file
def read_unlock_file (searchfolder):
	datafolder = os.path.join (searchfolder, "Data")
	if (os.path.isdir (datafolder)):
		readfile = os.path.join (datafolder, "Unlocks.dat")
	else:
		home = os.path.expanduser ("~")
		readfile = os.path.join (home, "Unlocks.dat")

	if not os.path.isfile (readfile):
		print >> sys.stderr, "File \"%s\" does not exist or could not be read." % readfile
		return False

	try:
		file = open (readfile, 'r')
	except IOError:
		print >> sys.stderr, "File \"%s\" could not be read." % readfile
		return False
	
	print "Read File: %s" % readfile
	readline = file.readline ()
	group = group_collection[0]
	temp = [song.name_trans for song in group.songs]
	full_temp = list (group.songs)

	# Read in the unlock codes, check that the songs listed exist,
	# and change the Song objects with the values in the unlock code
	while readline:
		changes = [0, 0, 0, 0, 0]
		readline = readline.strip ()
		if not readline:
			readline = file.readline ()
			continue
		elif readline.startswith ("//"):
			readline = file.readline ()
			continue
		elif readline.find ("#UNLOCK:") == -1:
			readline = file.readline ()
			continue
		unlock, parsedline = readline.split ("#UNLOCK:", 1)
		parsedline = parsedline.strip ()
		title, stats = parsedline.rsplit (':', 1)
		stats = stats.rstrip (';')
		stat_types = stats.split (',')
		for stat in stat_types:
#			print stat
			if stat[0:3] == "AP=":
				changes[0] = int(stat.lstrip("AP="))
			elif stat[0:3] == "CS=":
				changes[1] = int(stat.lstrip("CS="))
			elif stat[0:3] == "DP=":
				changes[2] = int(stat.lstrip("DP="))
			elif stat[0:3] == "RO=":
				changes[3] = int(stat.lstrip("RO="))
			elif stat[0:3] == "SP=":
				changes[4] = int(stat.lstrip("SP="))

		try:
			index = temp.index (title)
			current_song = full_temp[index]
			current_song.unlock_values (changes)
			temp.pop (index)
			full_temp.pop (index)
		except ValueError:
			print >> sys.stderr, "Song \"%s\" is not in your Songs folder." % title

		readline = file.readline()
	return True

# If running on Windows, write output and error messages to text files.
# Needed due to py2exe
if sys.platform == 'win32':
	sys.stdout = open ("log.txt", 'w')
	sys.stderr = open ("errors.log", 'w')

# Prints the help menu
def usage():
	print "%(app_name)s %(version)s" % {'app_name': APP_NAME, 'version': VERSION_NUMBER}
	if sys.platform == 'win32':
		print "Usage: stepmania-unlock-code-genenerator.exe [option]\n"
	else:
		print "Usage: step-unlock-code-gen [option]\n"
	print "Options are:"
	print "  -d, --dir <directory>    Directly load files from specified directory"
	print "  -h, --help               Display help text and exit"
	print "  -v, --version            Print version number and exit"
	sys.exit (42)

# Prints the application version number
def printVersion ():
	print "Version %s" % VERSION_NUMBER
	sys.exit (42)

# Parse any command line arguments
def parseArguments ():
	directory = ""
	skip = False

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hd:v", ["help", "dir=", "version"])
	except getopt.GetoptError, [msg, opt]:
		print >> sys.stderr, "Invalid argument passed: %s" % opt
		print >> sys.stderr, "Displaying help text and quitting\n"
		usage()
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage ()
		elif opt in ("-d", "--dir"):
			directory = arg
			skip = True
		elif opt in ("-v", "--version"):
			printVersion ()
	return directory, skip


# Main application
if __name__ == '__main__':
	directory, skip = parseArguments ()
	steplock = StepManiaLocker (directory)
	gtk.gdk.threads_init ()
	if skip:
		steplock.start_load_thread (steplock.load_button, skip)
	gtk.main ()

