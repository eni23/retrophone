#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function

from pprint import pprint
import sys
import time
import struct
import serial
import pygtk
import glob
pygtk.require('2.0')
import vte
import gtk


DEVS = [
    "/dev/ttyUSB*",
    "/dev/ttyACM*",
    "/dev/ttyS*",
]

# the gui
class RingerTestGui( gtk.Window ):

    def __init__( self ):

        super( RingerTestGui, self ).__init__()

        self.is_enabled = False
        self.volume = 0
        self.frequency = 0
        self.pause = 0
        self.count = 0

        self.set_title( "Ringer" )
        self.set_size_request( 500, 230 )
        self.set_position( gtk.WIN_POS_CENTER )

        self.fix = gtk.Fixed()
        self.add(self.fix)

        """devlist=[]
        for dev in DEVS:
            devlist.extend(glob.glob(dev))
        model = gtk.ListStore(str)
        combo = gtk.ComboBox()
        for itm in devlist:
            model.append([itm])
        combo.set_model(model)
        cell = gtk.CellRendererText()
        combo.pack_start(cell)
        combo.add_attribute(cell, 'text', 0)
        renderer = gtk.CellRendererText()
        combo.set_active(0)
        combo.pack_start(renderer, True)
        combo.add_attribute(renderer, 'text', 1)
        self.fix.put( combo, 120, 175 )"""

        self.term = vte.Terminal ()
        #v.connect ("child-exited", lambda term: gtk.main_quit())
        self.term.fork_command()
        self.term.feed_child('PS1=""\n')
        self.term.feed_child('clear\n')
        self.term.set_size_request( 200, 200 )
        self.fix.put( self.term, 285, 10 )



        self.scale_vol   = self.build_scale(
            "Volume",
            self.change_vol_cb,
            10,
            0,
            254
        )
        self.scale_freq  = self.build_scale(
            "Frequency",
            self.change_freq_cb,
            50,
            0,
            1000
        )
        self.scale_pause = self.build_scale(
            "Pause",
            self.change_pause_cb,
            90,
            0,
            5000
        )
        self.scale_count = self.build_scale(
            "Count",
            self.change_count_cb,
            130,
            0,
            80,
        )
        self.button, self.button_label, self.button_img = self.build_button(
            "enable",
            self.btn_click_cb
        )
        self.connect(
            "destroy",
            self.quit
        )
        self.fix.put( self.button, 15, 175 )
        b2 = gtk.Button("fetch config")
        b2.connect(
            "clicked",
            self.send_cfg_cb,
            None
        )
        self.fix.put( b2, 130, 175 )


        self.show_all()



    def build_button( self, caption, callback, image = gtk.STOCK_YES):
        button = gtk.Button()
        button_box = gtk.HBox( False, 0 )
        button_img = gtk.image_new_from_stock(
            image,
            gtk.ICON_SIZE_BUTTON
        )
        button_box.pack_start(
            button_img,
            False,
            False,
            3
        )
        button_label = gtk.Label( caption )
        button_box.pack_start(
            button_label,
            False,
            False,
            3
        )
        button.add( button_box )
        button.connect(
            "clicked",
            callback,
            None
        )
        return button, button_label, button_img


    def build_scale( self,
                     caption,
                     callback,
                     pos,
                     min_value  = 0,
                     max_value  = 254,
                     init_value = 0,
                     inc_value  = [ 1, 10 ],
                     width      = 180,
                     height     = 40
                    ):
        scale = gtk.HScale()
        scale.set_range(
            min_value,
            max_value
        )
        scale.set_increments(
            inc_value[0], inc_value[1]
        )
        scale.set_digits( 0 )
        scale.set_value( float(init_value) )
        scale.set_size_request( width, height )
        scale.connect( "value-changed", callback )
        self.fix.put(
            gtk.Label( caption ),
            15,
            pos + 18
        )
        self.fix.put( scale, 90, pos )
        return scale



    def btn_click_cb(self, widget, data=False):
        if self.is_enabled:
            self.is_enabled = False
            self.button_img.set_from_stock(
                gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON
            )
            self.button_label.set_text("enable")
        else:
            self.is_enabled = True
            self.button_img.set_from_stock(
                gtk.STOCK_NO, gtk.ICON_SIZE_BUTTON
            )
            self.button_label.set_text("disable")
        try:
            self.btn_click()
        except AttributeError:
            pass


    def change_vol_cb(self, widget):
        self.volume = int(widget.get_value())
        try:
            self.vol_change(self.volume)
        except AttributeError:
            pass


    def change_freq_cb(self, widget):
        self.frequency = int(widget.get_value())
        try:
            self.freq_change(self.frequency)
        except AttributeError:
            pass


    def change_pause_cb(self, widget):
        self.pause = int(widget.get_value())
        try:
            self.pause_change(self.pause)
        except AttributeError:
            pass

    def change_count_cb(self, widget):
        self.count = int(widget.get_value())
        try:
            self.count_change(self.count)
        except AttributeError:
            pass


    def quit(self, w=False):
        gtk.main_quit()


    def update_scales(self):
        self.scale_vol.set_value(float(self.volume))
        self.scale_freq.set_value(float(self.frequency))
        self.scale_pause.set_value(float(self.pause))
        self.scale_count.set_value(float(self.count))


    def send_cfg_cb(self, ww=False, w=False):
        self.fetch_config()


class RingerTestApp(RingerTestGui):

    def __init__(self):
        super(RingerTestApp, self).__init__()
        self.limit_data = {}
        self.init_ok = False
        self.init_serial()
        time.sleep(2)
        self.fetch_config()
        self.update_scales()
        self.init_ok = True

    def main(self):
        gtk.main()

    def ringer_on(self):
        msg = struct.pack("=B", 2)
        self.serial.write(msg)

    def ringer_on(self):
        msg = struct.pack("=B", 3)
        self.serial.write(msg)

    def init_serial(self):
        try:
            self.serial = serial.Serial(
                port='/dev/ttyUSB0',
                baudrate=19200
            )
        except:
            print("ERROR: Opening serial port failed")
            sys.exit(1)

        self.serial.isOpen()
        time.sleep(0.1)


    def fetch_config(self):
        msg = struct.pack("=B", 4)
        self.serial.write(msg)
        time.sleep(0.1)
        data = self.serial.read(7)
        res = struct.unpack("=BHHH", data)
        self.volume = res[0]
        self.frequency = res[1]
        self.pause = res[2]
        self.count = res[3]
        self.term.feed("cfg {0}\n\r".format(res))


    def send_config(self):
        self.serial.flush()
        if self.volume > 254:
            self.volume=254
        bin_cfg = struct.pack("=BHHH", self.volume, self.frequency, self.pause, self.count )
        cmd = struct.pack("=B", 5)
        self.serial.write(cmd)
        time.sleep(0.01)
        res = self.serial.read(1)
        nres = struct.unpack("=B", res)
        if nres[0]==13:
            self.serial.write(bin_cfg)
            time.sleep(0.01)
            xres = self.serial.read(1)
            xxres = struct.unpack("=B", xres)
            if xxres[0] == 222:
                self.term.feed("config OK\n\r")
            else:
                self.term.feed("config ERR\n\r")


    def millis(self):
        return int(round(time.time() * 1000))


    def limit(self, id, every_ms ):
        now = self.millis()
        try:
            dbdata = self.limit_data[str(id)]
        except KeyError:
            self.limit_data[str(id)] = 0
            dbdata = 0
        if dbdata < (now - every_ms):
            self.limit_data[str(id)] = now
            return True
        else:
            return False


    def limit_update(self):
        if not self.init_ok:
            return
        if ( self.limit(0, 180) ):
            self.send_config()


    def btn_click(self):
        if self.is_enabled:
            msg = struct.pack("=B", 1)
        else:
            msg = struct.pack("=B", 2)
        self.serial.write(msg)
        time.sleep(0.1)


    def freq_change(self, val):
        self.frequency = int(val)
        self.limit_update()

    def vol_change(self, val):
        self.volume = int(val)
        self.limit_update()#self.send_config()

    def pause_change(self, val):
        self.pause = int(val)
        self.limit_update()#self.send_config()

    def count_change(self, val):
        self.count = int(val)
        self.limit_update()#self.send_config()


if __name__ == "__main__":
    try:
        app = RingerTestApp()
        app.main()
    except KeyboardInterrupt:
        sys.exit(0)
