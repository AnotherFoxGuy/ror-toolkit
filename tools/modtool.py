#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys, os, os.path, shutil

if sys.platform in ['linux', 'linux2']:
	sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib_common"))
	sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib_linux"))
elif sys.platform in ['win32']:
	sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib_common"))
	sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib_windows"))

from ror.logger import log
from ror.settingsManager import getSettingsManager

def usage():
	print "usage (general): %s <mode> <additionaloptions> [--verbose] [--dryrun]" % (os.path.basename(sys.argv[0]))
	print "list <filename>"
	print " list all found and valid modifications in filename"
	print ""
	print "listall <filename> --verbose"
	print " list all found modifications in filename (valid and invalid)"
	print ""
	print "installall <filename> --verbose --dryrun"
	print " install all found modifications in filename"
	print ""
	print "installrepo <filename> --verbose --dryrun"
	print " install all found modifications in filename that is downloaded from the repository"
	print ""
	print "install <filename> <modification> --verbose --dryrun"
	print " install a certain modifications in filename (valid and invalid)"
	print ""
	print "listinstalled"
	print " lists all installed RoR Mods"
	print ""
	print "uninstall <modname> --verbose --dryrun"
	print " uninstalls a mod"
	print ""
	print "uniqueid new"
	print " get a new id from the repository"
	print ""
	print "createmod <truck filename>"
	print " creates a new mod using the new ID format"
	print ""
	print "notes: the --verbose option is optional to increase the output for debugging"
	print "       the --dryrun option is optional and prints out what would be done"
	sys.exit(0)

def main():
	# check for valid RoR Directory!
	import ror.rorcommon
	if not ror.rorcommon.checkRoRDirectory():
		import ror.starter
		ror.starter.startApp()

	if len(sys.argv) < 2:
		usage()

	mode = sys.argv[1]
	if not mode in ['list', 'listall', 'install', 'installall', 'listinstalled','uninstall', 'installrepo', 'uniqueid', 'createmod']:
		usage()
	if len(sys.argv) < 4 and mode in ['install']:
		usage()

	if mode in ['list', 'listall', 'install', 'installall']:
		targetfile = sys.argv[2]
		if not os.path.isfile(targetfile):
			log().error("%s is not a valid target filename!" % targetfile)
			usage()
	elif mode in ['listinstalled']:
		targetfile = rorpath
	elif mode in ['installrepo']:
		targetfile = sys.argv[2]
	elif mode == 'uninstall':
		targetfile = sys.argv[2]
	elif mode == 'createmod':
		targetfile = sys.argv[2]
	elif mode == 'uniqueid':
		targetfile = ''

	# get optional flags
	verbose = False
	dryrun = False
	for option in sys.argv:
		if option == "--verbose":
			verbose = True
		if option == "--dryrun":
			dryrun = True

	if len(sys.argv) == 4:
		installtarget = sys.argv[3]
	else:
		installtarget = None
	import ror.modtool
	result = ror.modtool.ModTool().work(mode, targetfile, verbose, dryrun, installtarget)


if __name__=="__main__":
	main()
