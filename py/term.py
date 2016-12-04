#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function


try:
  import gtk
except:
  print >> sys.stderr, "You need to install the python gtk bindings"
  sys.exit(1)

# import vte
try:
  import vte
except:
  error = gtk.MessageDialog (None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK,
    'You need to install python bindings for libvte')
  error.run()
  sys.exit (1)

if __name__ == '__main__':
  v = vte.Terminal ()
  v.connect ("child-exited", lambda term: gtk.main_quit())
  v.fork_command()
  v.set_size_request(100,100)
  v.feed('echo "Hello World"\n')
  window = gtk.Window()
  window.add(v)
  window.connect('delete-event', lambda window, event: gtk.main_quit())
  window.show_all()
  gtk.main()
