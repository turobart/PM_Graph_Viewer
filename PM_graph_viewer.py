'''
Author: Bartłomiej Turowski
International Research Centre MagTop, Institute of Physics, Polish Academy of Sciences
Aleja Lotnikow 32/46, PL-02668 Warsaw, Poland
Date: 13.07.2018
'''

# -*- coding: utf-8 -*-

import wx
import math
from matplotlib import pyplot as plt
import datetime
import os.path
import gc
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import dateutil
import matplotlib.dates as md
import wx.lib.scrolledpanel as scrolled
import sys
from matplotlib.widgets import Cursor

old_plot_window=None
water_window=None

time_list=[]
water_list=[]
temp1_list=[]
temp2_list=[]

values=[0,0,0]

size_x=285+35+20
size_y=60+50+50+5

currentDirectory=os.path.dirname(os.path.realpath(__file__))

data_path = getattr(sys, '_MEIPASS', os.getcwd())

# IDs for GUI
APP_EXIT=1
ID_PLOT=2
ID_WATER=3
ID_INFO=4
ID_TURBO=5
ID_P1=6
ID_P2=7
ID_PLOT_SETUP=8
ID_W_C=9
ID_T_C=10
ID_P_RPS_C=11
ID_C_C=12
ID_W_C_M=13
ID_T_C_M=14
ID_P_RPS_C_M=15
ID_C_C_M=16
ID_CURSOR=17
ID_TB=18
ID_T1=19
ID_T2=20
ID_T3=21
ID_T4=22
ID_T5=23
ID_T6=24
ID_T7=25
ID_T8=26
ID_T9=27
ID_T10=28
ID_T11=29
ID_T12=30
ID_P_VA_C=31
ID_P_VA_C_M=32
ID_TLBR=33


class main_window(wx.Frame):
  
    def __init__(self, parent, title):
        super(main_window, self).__init__(parent, title=title, size=(size_x, size_y))
          
        self.InitUI()    
        self.Centre()
        self.Show()    
        
    def InitUI(self):
        self.cell_size=(85,20+40+40)
        
        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()

        self.water_plot = wx.MenuItem(self.fileMenu, ID_PLOT, '&Show plot\tCtrl+O')
        self.cursor_line = wx.MenuItem(self.fileMenu, ID_CURSOR, 'Cursor crosshair', kind=wx.ITEM_CHECK)
        self.tlbr = wx.MenuItem(self.fileMenu, ID_TLBR, 'Show toolbar',kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.ToggleToolBar, self.tlbr)
        self.Bind(wx.EVT_MENU, self.OldPlot, id=ID_PLOT)
        self.Bind(wx.EVT_MENU, self.cursor_endis, id=ID_CURSOR)
        
        self.qmi = wx.MenuItem(self.fileMenu, APP_EXIT, '&Quit\tCtrl+Q')
        
        self.fileMenu.Append(self.water_plot)
        self.fileMenu.Append(self.cursor_line)
        self.fileMenu.AppendSeparator()
        self.fileMenu.Append(self.tlbr)
        self.fileMenu.AppendSeparator()
        self.fileMenu.Append(self.qmi)
        
        self.fileMenu.Check(ID_CURSOR, False)
        self.fileMenu.Check(ID_TLBR, True)
        
        self.plot_menu = wx.Menu(ID_PLOT_SETUP)
        self.water_check=wx.MenuItem(self.plot_menu, ID_W_C, 'Water flow', kind=wx.ITEM_CHECK)
        self.temp_check=wx.MenuItem(self.plot_menu, ID_T_C, 'Water temperature', kind=wx.ITEM_CHECK)
        self.turbo_pump_check=wx.MenuItem(self.plot_menu, ID_P_RPS_C, 'Turbo pumps RPS', kind=wx.ITEM_CHECK)
        self.turbo_pumpVA_check=wx.MenuItem(self.plot_menu, ID_P_VA_C, 'Turbo pumps VA', kind=wx.ITEM_CHECK)
        self.cryo_pump_check=wx.MenuItem(self.plot_menu, ID_C_C, 'Cryo pumps', kind=wx.ITEM_CHECK)
        self.plot_menu.Append(self.water_check)
        self.plot_menu.Append(self.temp_check)
        self.plot_menu.Append(self.turbo_pump_check)
        self.plot_menu.Append(self.turbo_pumpVA_check)
        self.plot_menu.Append(self.cryo_pump_check)
        
        self.Bind(wx.EVT_MENU, self.off_axis, id=ID_W_C)
        self.Bind(wx.EVT_MENU, self.off_axis, id=ID_T_C)
        self.Bind(wx.EVT_MENU, self.off_axis, id=ID_P_RPS_C)
        self.Bind(wx.EVT_MENU, self.off_axis, id=ID_P_VA_C)
        self.Bind(wx.EVT_MENU, self.off_axis, id=ID_C_C)
        
        self.plot_menu.Check(ID_W_C, False)
        self.plot_menu.Check(ID_T_C, True) 
        self.plot_menu.Check(ID_P_RPS_C, True)
        self.plot_menu.Check(ID_P_VA_C, True)
        self.plot_menu.Check(ID_C_C, True)
        self.water_check.Enable(False)
        
        self.main_plot_menu = wx.Menu(ID_PLOT_SETUP)
        self.main_water_check=wx.MenuItem(self.plot_menu, ID_W_C_M, 'Water flow', kind=wx.ITEM_RADIO)
        self.main_temp_check=wx.MenuItem(self.main_plot_menu, ID_T_C_M, 'Water temperature', kind=wx.ITEM_RADIO)
        self.main_turbo_pump_check=wx.MenuItem(self.main_plot_menu, ID_P_RPS_C_M, 'Turbo pumps RPS', kind=wx.ITEM_RADIO)
        self.main_turbo_pumpVA_check=wx.MenuItem(self.main_plot_menu, ID_P_VA_C_M, 'Turbo pumps VA', kind=wx.ITEM_RADIO)
        self.main_cryo_pump_check=wx.MenuItem(self.main_plot_menu, ID_C_C_M, 'Cryo pumps', kind=wx.ITEM_RADIO)
        self.main_plot_menu.Append(self.main_water_check)
        self.main_plot_menu.Append(self.main_temp_check)
        self.main_plot_menu.Append(self.main_turbo_pump_check)
        self.main_plot_menu.Append(self.main_turbo_pumpVA_check)
        self.main_plot_menu.Append(self.main_cryo_pump_check)
        self.main_plot_menu.Check(ID_W_C_M, True) 
        self.Bind(wx.EVT_MENU, self.main_axis, id=ID_W_C_M)
        self.Bind(wx.EVT_MENU, self.main_axis, id=ID_T_C_M)
        self.Bind(wx.EVT_MENU, self.main_axis, id=ID_P_RPS_C_M)
        self.Bind(wx.EVT_MENU, self.main_axis, id=ID_P_VA_C_M)
        self.Bind(wx.EVT_MENU, self.main_axis, id=ID_C_C_M)
        
        self.info_menu = wx.Menu(ID_INFO)
        
        self.menubar.Append(self.fileMenu, '&Menu')
        self.menubar.Append(self.main_plot_menu, '&Main setup')
        self.menubar.Append(self.plot_menu, '&Plot setup')
        self.menubar.Append(self.info_menu, '&Info')
        
        self.Bind(wx.EVT_MENU_OPEN, self.menuAction)

        self.SetMenuBar(self.menubar)
        
        self.main_panel = wx.Panel(self)
        self.main_panel.SetBackgroundColour('#ffffff')
        toolbar_sizer=wx.BoxSizer(wx.VERTICAL)
        
        self.separator_panel = wx.Panel(self, size=(size_x,5))
        self.separator_panel.SetBackgroundColour('#ffffff')
        
        text_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD)
        unit_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL)
        number_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.NORMAL) 
        small_font = wx.Font(6, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD)    
        
        os.chdir(data_path)
        self.toolbar = wx.ToolBar(self, id=ID_TB)
        self.toolbar.SetToolBitmapSize((40,40))
        self.graphTL=self.toolbar.AddTool(ID_T1, '', wx.Bitmap('graph.png'), shortHelp='Show graph')
        self.toolbar.AddSeparator()
        self.toolbar.AddSeparator()
        self.toolbar.AddSeparator()
        water_flowTL_main=self.toolbar.AddRadioTool(ID_T2, '', wx.Bitmap('water_flow.png'), shortHelp='Water flow')
        water_tempTL_main=self.toolbar.AddRadioTool(ID_T3, '', wx.Bitmap('water_temp.png'), shortHelp='Water temperature')
        turbo_pumpTL_RPS_main=self.toolbar.AddRadioTool(ID_T4, '', wx.Bitmap('turbo_pumpRPS.png'), shortHelp='Turbo pump RPS')
        turbo_pumpTL_VA_main=self.toolbar.AddRadioTool(ID_T5, '', wx.Bitmap('turbo_pumpVA.png'), shortHelp='Turbo pump VA')
        cryo_tempTL_main=self.toolbar.AddRadioTool(ID_T6, '', wx.Bitmap('cryo_temp.png'), shortHelp='Cryo pump temperature')       
        self.toolbar.AddSeparator()
        
        self.Bind(wx.EVT_TOOL, self.OldPlot, self.graphTL)
        self.Bind(wx.EVT_TOOL, self.png_buttons_main, water_flowTL_main)
        self.Bind(wx.EVT_TOOL, self.png_buttons_main, water_tempTL_main)
        self.Bind(wx.EVT_TOOL, self.png_buttons_main, turbo_pumpTL_RPS_main)
        self.Bind(wx.EVT_TOOL, self.png_buttons_main, turbo_pumpTL_VA_main)
        self.Bind(wx.EVT_TOOL, self.png_buttons_main, cryo_tempTL_main)
        
        self.toolbar.Realize() 
        
        self.toolbar2 = wx.ToolBar(self, id=ID_TB)
        self.toolbar2.SetToolBitmapSize((40,40))
        self.cursorTL=self.toolbar2.AddCheckTool(ID_T7, '', wx.Bitmap('cursor.png'), shortHelp='Turn the cursor on/off')
        self.toolbar2.AddSeparator()
        self.toolbar2.AddSeparator()
        self.toolbar2.AddSeparator()
        water_flowTL_off=self.toolbar2.AddCheckTool(ID_T8, '', wx.Bitmap('water_flow.png'), shortHelp='Water flow')
        water_tempTL_off=self.toolbar2.AddCheckTool(ID_T9, '', wx.Bitmap('water_temp.png'), shortHelp='Water temperature')
        turbo_pumpTL_RPS_off=self.toolbar2.AddCheckTool(ID_T10, '', wx.Bitmap('turbo_pumpRPS.png'), shortHelp='Turbo pump RPS')
        turbo_pumpTL_VA_off=self.toolbar2.AddCheckTool(ID_T11, '', wx.Bitmap('turbo_pumpVA.png'), shortHelp='Turbo pump VA')
        cryo_tempTL_off=self.toolbar2.AddCheckTool(ID_T12, '', wx.Bitmap('cryo_temp.png'), shortHelp='Cryo pump temperature')       
        self.toolbar2.AddSeparator()
        self.Bind(wx.EVT_TOOL, self.cursor_endis, self.cursorTL)
        self.Bind(wx.EVT_TOOL, self.png_buttons_off, water_flowTL_off)
        self.Bind(wx.EVT_TOOL, self.png_buttons_off, water_tempTL_off)
        self.Bind(wx.EVT_TOOL, self.png_buttons_off, turbo_pumpTL_RPS_off)
        self.Bind(wx.EVT_TOOL, self.png_buttons_off, turbo_pumpTL_VA_off)
        self.Bind(wx.EVT_TOOL, self.png_buttons_off, cryo_tempTL_off)
        self.toolbar2.ToggleTool(ID_T8, False)
        self.toolbar2.ToggleTool(ID_T9, True)
        self.toolbar2.ToggleTool(ID_T10, True)
        self.toolbar2.ToggleTool(ID_T11, True)
        self.toolbar2.ToggleTool(ID_T12, True)
        self.toolbar2.Realize() 
        
        toolbar_sizer.Add(self.toolbar, 0, wx.EXPAND)
        toolbar_sizer.Add(self.separator_panel)
        toolbar_sizer.Add(self.toolbar2, 0, wx.EXPAND)
        
        self.SetSizer(toolbar_sizer)
        
        ico=wx.Icon('ikonaGW.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        
        self.SetMinSize((size_x, size_y))
        self.SetMaxSize((size_x, size_y))
        

    def ToggleToolBar(self, event):
        if self.tlbr.IsChecked():
            self.toolbar.Show()
            self.toolbar2.Show()
            self.main_panel.Show()
            self.separator_panel.Show()
            self.SetMinSize((size_x, size_y))
            self.SetSize((size_x, size_y))
        else:
            self.toolbar.Hide()
            self.toolbar2.Hide()
            self.main_panel.Hide()
            self.separator_panel.Hide()
            
            self.SetMaxSize((size_x, size_y))
            self.SetMinSize((size_x, 60))
            self.SetSize((size_x, 60))

    def cursor_endis(self, event):
        if event.GetId()==ID_T7:
            if self.toolbar2.GetToolState(ID_T7):
                self.fileMenu.Check(ID_CURSOR, True)
            else:
                self.fileMenu.Check(ID_CURSOR, False)
        else:
            if self.cursor_line.IsChecked():
                self.toolbar2.ToggleTool(ID_T7, True)
            else:
                self.toolbar2.ToggleTool(ID_T7, False)


    def main_axis(self, event):
        button_state=event.IsChecked()
        id=event.GetId()
        
        if button_state:
        
            if id==ID_W_C_M:
                self.plot_menu.Check(ID_W_C, False) 
                self.water_check.Enable(False)
                
                self.plot_menu.Check(ID_T_C, True)
                self.plot_menu.Check(ID_P_VA_C, True)
                self.plot_menu.Check(ID_P_RPS_C, True) 
                self.plot_menu.Check(ID_C_C, True)
                self.temp_check.Enable(True)
                self.turbo_pump_check.Enable(True)
                self.turbo_pumpVA_check.Enable(True)
                self.cryo_pump_check.Enable(True)
                
                self.toolbar.ToggleTool(ID_T2, True)
                
                self.toolbar2.ToggleTool(ID_T8, False)
                self.toolbar2.ToggleTool(ID_T9, True)
                self.toolbar2.ToggleTool(ID_T10, True)
                self.toolbar2.ToggleTool(ID_T11, True)
                self.toolbar2.ToggleTool(ID_T12, True)
                
                self.toolbar2.EnableTool(ID_T8, False)
                self.toolbar2.EnableTool(ID_T9, True)
                self.toolbar2.EnableTool(ID_T10, True)
                self.toolbar2.EnableTool(ID_T11, True)
                self.toolbar2.EnableTool(ID_T12, True)
            elif id==ID_T_C_M:
                self.plot_menu.Check(ID_T_C, False) 
                self.temp_check.Enable(False)
                
                self.plot_menu.Check(ID_W_C, True) 
                self.plot_menu.Check(ID_P_RPS_C, True)
                self.plot_menu.Check(ID_P_VA_C, True)
                self.plot_menu.Check(ID_C_C, True)
                self.water_check.Enable(True)
                self.turbo_pump_check.Enable(True)
                self.turbo_pumpVA_check.Enable(True)
                self.cryo_pump_check.Enable(True)
                
                self.toolbar.ToggleTool(ID_T3, True)
                
                self.toolbar2.ToggleTool(ID_T8, True)
                self.toolbar2.ToggleTool(ID_T9, False)
                self.toolbar2.ToggleTool(ID_T10, True)
                self.toolbar2.ToggleTool(ID_T11, True)
                self.toolbar2.ToggleTool(ID_T12, True)
                
                self.toolbar2.EnableTool(ID_T8, True)
                self.toolbar2.EnableTool(ID_T9, False)
                self.toolbar2.EnableTool(ID_T10, True)
                self.toolbar2.EnableTool(ID_T11, True)
                self.toolbar2.EnableTool(ID_T12, True)
            elif id==ID_P_RPS_C_M:
                self.plot_menu.Check(ID_P_RPS_C, False) 
                self.turbo_pump_check.Enable(False)
                
                self.plot_menu.Check(ID_W_C, True) 
                self.plot_menu.Check(ID_T_C, True) 
                self.plot_menu.Check(ID_C_C, True)
                self.plot_menu.Check(ID_P_VA_C, True)
                self.water_check.Enable(True)
                self.temp_check.Enable(True)
                self.turbo_pumpVA_check.Enable(True)
                self.cryo_pump_check.Enable(True)
                
                self.toolbar.ToggleTool(ID_T4, True)
                
                self.toolbar2.ToggleTool(ID_T8, True)
                self.toolbar2.ToggleTool(ID_T9, True)
                self.toolbar2.ToggleTool(ID_T10, False)
                self.toolbar2.ToggleTool(ID_T11, True)
                self.toolbar2.ToggleTool(ID_T12, True)
                
                self.toolbar2.EnableTool(ID_T8, True)
                self.toolbar2.EnableTool(ID_T9, True)
                self.toolbar2.EnableTool(ID_T10, False)
                self.toolbar2.EnableTool(ID_T11, True)
                self.toolbar2.EnableTool(ID_T12, True)
            elif id==ID_P_VA_C_M:
                self.plot_menu.Check(ID_P_VA_C, False) 
                self.turbo_pumpVA_check.Enable(False)
                
                self.plot_menu.Check(ID_W_C, True) 
                self.plot_menu.Check(ID_T_C, True) 
                self.plot_menu.Check(ID_C_C, True)
                self.plot_menu.Check(ID_P_RPS_C, True)
                self.water_check.Enable(True)
                self.temp_check.Enable(True)
                self.turbo_pump_check.Enable(True)
                self.cryo_pump_check.Enable(True)
                
                self.toolbar.ToggleTool(ID_T5, True)
                
                self.toolbar2.ToggleTool(ID_T8, True)
                self.toolbar2.ToggleTool(ID_T9, True)
                self.toolbar2.ToggleTool(ID_T10, True)
                self.toolbar2.ToggleTool(ID_T11, False)
                self.toolbar2.ToggleTool(ID_T12, True)
                
                self.toolbar2.EnableTool(ID_T8, True)
                self.toolbar2.EnableTool(ID_T9, True)
                self.toolbar2.EnableTool(ID_T10, True)
                self.toolbar2.EnableTool(ID_T11, False)
                self.toolbar2.EnableTool(ID_T12, True)    
            elif id==ID_C_C_M:
                self.plot_menu.Check(ID_C_C, False) 
                self.cryo_pump_check.Enable(False)
                
                self.plot_menu.Check(ID_W_C, True) 
                self.plot_menu.Check(ID_P_RPS_C, True)
                self.plot_menu.Check(ID_P_VA_C, True)
                self.plot_menu.Check(ID_T_C, True)
                self.water_check.Enable(True)
                self.temp_check.Enable(True)
                self.turbo_pump_check.Enable(True)
                self.turbo_pumpVA_check.Enable(True)
                
                self.toolbar.ToggleTool(ID_T6, True)
                
                self.toolbar2.ToggleTool(ID_T8, True)
                self.toolbar2.ToggleTool(ID_T9, True)
                self.toolbar2.ToggleTool(ID_T10, True)
                self.toolbar2.ToggleTool(ID_T11, True)
                self.toolbar2.ToggleTool(ID_T12, False)
                
                self.toolbar2.EnableTool(ID_T8, True)
                self.toolbar2.EnableTool(ID_T9, True)
                self.toolbar2.EnableTool(ID_T10, True)
                self.toolbar2.EnableTool(ID_T11, True)
                self.toolbar2.EnableTool(ID_T12, False)
    
    def off_axis(self, event):
        button_state=event.IsChecked()
        id=event.GetId()
        
        if id==ID_W_C:
            self.toolbar2.ToggleTool(ID_T8, button_state) 
        elif id==ID_T_C:
            self.toolbar2.ToggleTool(ID_T9, button_state)
        elif id==ID_P_RPS_C:
            self.toolbar2.ToggleTool(ID_T10, button_state)
        elif id==ID_P_VA_C:
            self.toolbar2.ToggleTool(ID_T11, button_state)
        elif id==ID_C_C:
            self.toolbar2.ToggleTool(ID_T12, button_state)
        
    def png_buttons_main(self, event):
        id=event.GetId()
        button_state=self.toolbar.GetToolState(id)
        
        if button_state:
        
            if id==ID_T2:
                self.toolbar2.ToggleTool(ID_T8, False)
                self.toolbar2.ToggleTool(ID_T9, True)
                self.toolbar2.ToggleTool(ID_T10, True)
                self.toolbar2.ToggleTool(ID_T11, True)
                self.toolbar2.ToggleTool(ID_T12, True)
                
                self.toolbar2.EnableTool(ID_T8, False)
                self.toolbar2.EnableTool(ID_T9, True)
                self.toolbar2.EnableTool(ID_T10, True)
                self.toolbar2.EnableTool(ID_T11, True)
                self.toolbar2.EnableTool(ID_T12, True)
                
                self.main_plot_menu.Check(ID_W_C_M, True)
                
                self.plot_menu.Check(ID_W_C, False) 
                self.water_check.Enable(False) 
                
                self.plot_menu.Check(ID_T_C, True)
                self.plot_menu.Check(ID_P_RPS_C, True)
                self.plot_menu.Check(ID_P_VA_C, True) 
                self.plot_menu.Check(ID_C_C, True)
                
                self.temp_check.Enable(True)
                self.turbo_pump_check.Enable(True)
                self.turbo_pumpVA_check.Enable(True)
                self.cryo_pump_check.Enable(True)
            elif id==ID_T3:
                self.toolbar2.ToggleTool(ID_T8, True)
                self.toolbar2.ToggleTool(ID_T9, False)
                self.toolbar2.ToggleTool(ID_T10, True)
                self.toolbar2.ToggleTool(ID_T11, True)
                self.toolbar2.ToggleTool(ID_T12, True)
                
                self.toolbar2.EnableTool(ID_T8, True)
                self.toolbar2.EnableTool(ID_T9, False)
                self.toolbar2.EnableTool(ID_T10, True)
                self.toolbar2.EnableTool(ID_T11, True)
                self.toolbar2.EnableTool(ID_T12, True)
                
                self.main_plot_menu.Check(ID_T_C_M, True)
                
                self.plot_menu.Check(ID_T_C, False) 
                self.temp_check.Enable(False)
                 
                self.plot_menu.Check(ID_W_C, True) 
                self.plot_menu.Check(ID_P_RPS_C, True)
                self.plot_menu.Check(ID_P_VA_C, True) 
                self.plot_menu.Check(ID_C_C, True)
                
                self.water_check.Enable(True)
                self.turbo_pump_check.Enable(True)
                self.turbo_pumpVA_check.Enable(True)
                self.cryo_pump_check.Enable(True)
            elif id==ID_T4:
                self.toolbar2.ToggleTool(ID_T8, True)
                self.toolbar2.ToggleTool(ID_T9, True)
                self.toolbar2.ToggleTool(ID_T10, False)
                self.toolbar2.ToggleTool(ID_T11, True)
                self.toolbar2.ToggleTool(ID_T12, True)
                
                self.toolbar2.EnableTool(ID_T8, True)
                self.toolbar2.EnableTool(ID_T9, True)
                self.toolbar2.EnableTool(ID_T10, False)
                self.toolbar2.EnableTool(ID_T11, True)
                self.toolbar2.EnableTool(ID_T12, True)
                
                self.main_plot_menu.Check(ID_P_RPS_C_M, True)
                
                self.plot_menu.Check(ID_P_RPS_C, False) 
                self.turbo_pump_check.Enable(False)
                 
                self.plot_menu.Check(ID_W_C, True) 
                self.plot_menu.Check(ID_T_C, True)
                self.plot_menu.Check(ID_P_VA_C, True)
                self.plot_menu.Check(ID_C_C, True)
                
                self.water_check.Enable(True)
                self.temp_check.Enable(True)
                self.turbo_pumpVA_check.Enable(True)
                self.cryo_pump_check.Enable(True)
            elif id==ID_T5:
                self.toolbar2.ToggleTool(ID_T8, True)
                self.toolbar2.ToggleTool(ID_T9, True)
                self.toolbar2.ToggleTool(ID_T10, True)
                self.toolbar2.ToggleTool(ID_T11, False)
                self.toolbar2.ToggleTool(ID_T12, True)
                
                self.toolbar2.EnableTool(ID_T8, True)
                self.toolbar2.EnableTool(ID_T9, True)
                self.toolbar2.EnableTool(ID_T10, True)
                self.toolbar2.EnableTool(ID_T11, False)
                self.toolbar2.EnableTool(ID_T12, True)
                
                self.main_plot_menu.Check(ID_P_VA_C_M, True)
                
                self.plot_menu.Check(ID_P_VA_C, False) 
                self.turbo_pumpVA_check.Enable(False)
                 
                self.plot_menu.Check(ID_W_C, True) 
                self.plot_menu.Check(ID_T_C, True)
                self.plot_menu.Check(ID_P_RPS_C, True)
                self.plot_menu.Check(ID_C_C, True)
                
                self.water_check.Enable(True)
                self.temp_check.Enable(True)
                self.turbo_pump_check.Enable(True)
                self.cryo_pump_check.Enable(True)
            elif id==ID_T6:
                self.toolbar2.ToggleTool(ID_T8, True)
                self.toolbar2.ToggleTool(ID_T9, True)
                self.toolbar2.ToggleTool(ID_T10, True)
                self.toolbar2.ToggleTool(ID_T11, True)
                self.toolbar2.ToggleTool(ID_T12, False)
                
                self.toolbar2.EnableTool(ID_T8, True)
                self.toolbar2.EnableTool(ID_T9, True)
                self.toolbar2.EnableTool(ID_T10, True)
                self.toolbar2.EnableTool(ID_T11, True)
                self.toolbar2.EnableTool(ID_T12, False)
                
                self.main_plot_menu.Check(ID_C_C_M, True)
                
                self.plot_menu.Check(ID_C_C, False) 
                self.cryo_pump_check.Enable(False)
                 
                self.plot_menu.Check(ID_W_C, True) 
                self.plot_menu.Check(ID_P_RPS_C, True)
                self.plot_menu.Check(ID_P_VA_C, True)
                self.plot_menu.Check(ID_T_C, True)
                
                self.water_check.Enable(True)
                self.temp_check.Enable(True)
                self.turbo_pump_check.Enable(True)
                self.turbo_pumpVA_check.Enable(True)
                
    def png_buttons_off(self, event):
        id=event.GetId()
        button_state=self.toolbar2.GetToolState(id)
   
        if id==ID_T8:
            self.plot_menu.Check(ID_W_C, button_state) 
        elif id==ID_T9:
            self.plot_menu.Check(ID_T_C, button_state)
        elif id==ID_T10:
            self.plot_menu.Check(ID_P_RPS_C, button_state)
        elif id==ID_T11:
            self.plot_menu.Check(ID_P_VA_C, button_state)
        elif id==ID_T12:
            self.plot_menu.Check(ID_C_C, button_state)
    
    def menuAction(self, event):
        if event.GetMenu() == self.info_menu:
            self.infoWindow(event)
            
    def infoWindow(self, event):
            info_window(main_frame, title="Info")
        
    def OldPlot(self, event):
        global current_background,old_background, bg_window
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=currentDirectory, 
            defaultFile="",
            wildcard='txt files (*.txt)|*.txt',
            style=wx.FD_OPEN| wx.FD_CHANGE_DIR|wx.FD_FILE_MUST_EXIST
            )
        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            for path in paths:
                with open(path) as old_plot_file:
                    data = old_plot_file.read()
                    data = data.split('\n')
                    data_org=data
                    data=data[2:len(data)-1]
                    
                    global OP_time, OP_t1, OP_t2, OP_water, OP_p1_RPS, OP_p2_RPS, old_plot_window
                    global OP_top, OP_buffer, OP_side, OP_LL, OP_p1_VA, OP_p2_VA
                    OP_p1_RPS=None
                    OP_p2_RPS=None
                    OP_p1_VA=None
                    OP_p2_VA=None
                    OP_side=None
                    OP_LL=None
                    OP_top=None
                    OP_buffer=None
                    tt = [(row.split('\t')[0]) for row in data]
                    OP_time = [dateutil.parser.parse(s) for s in tt]
                    OP_t1 = [float(row.split('\t')[1]) for row in data]
                    OP_t2 = [float(row.split('\t')[2]) for row in data]
                    OP_water = [float(row.split('\t')[3]) for row in data]
                    
                    headers_data = data_org[0].split('\t')
                    
                    if ('LL pump') in headers_data:
                        LL_pump_index = data_org[0].split('\t').index('LL pump')-1 #double \t after Time
                        OP_p1_RPS = [float(row.split('\t')[LL_pump_index]) for row in data]
#                         col=5
                    if ('PM pump') in headers_data:
                        PM_pump_index = data_org[0].split('\t').index('PM pump')-1 
                        OP_p2_RPS = [float(row.split('\t')[PM_pump_index]) for row in data]
#                         col=6
                    if ('LL VA') in headers_data: 
                        LL_VA_pump_index = data_org[0].split('\t').index('LL VA')-1 
                        OP_p1_VA = [float(row.split('\t')[LL_VA_pump_index]) for row in data]
                    if ('PM VA') in headers_data: 
                        PM_VA_pump_index = data_org[0].split('\t').index('PM VA')-1 
                        OP_p2_VA = [float(row.split('\t')[PM_VA_pump_index]) for row in data]
                    if ('C side') in headers_data: 
                        side_pump_index = data_org[0].split('\t').index('C side')-1 
                        OP_side = [float(row.split('\t')[side_pump_index]) for row in data]
                    if ('C top') in headers_data: 
                        top_pump_index = data_org[0].split('\t').index('C top')-1 
                        OP_top = [float(row.split('\t')[top_pump_index]) for row in data]
                    if ('C buff') in headers_data: 
                        buffer_pump_index = data_org[0].split('\t').index('C buff')-1 
                        OP_buffer = [float(row.split('\t')[buffer_pump_index]) for row in data]
                    elif ('C buffer') in headers_data: 
                        buffer_pump_index = data_org[0].split('\t').index('C buffer')-1 
                        OP_buffer = [float(row.split('\t')[buffer_pump_index]) for row in data]
                    if ('C load lock') in headers_data: 
                        LL_C_pump_index = data_org[0].split('\t').index('C load lock')-1 
                        OP_LL = [float(row.split('\t')[LL_C_pump_index]) for row in data]
                    
                    old_plot_window=MatplotPanel(main_frame, title=os.path.basename(os.path.normpath(path)))
            dlg.Destroy()
            gc.collect()       

class MatplotPanel(wx.Frame):
    
    def __init__(self, parent, title):
        super(MatplotPanel, self).__init__(parent, title=title, size=(735, 415))
        
        self.InitUI()    
        self.Show()
        
    def InitUI(self):
        global OP_time, OP_t1, OP_t2, OP_water, OP_p1_RPS, OP_p2_RPS, OP_top, OP_buffer, OP_side, OP_p1_VA, OP_p2_VA, OP_LL
        self.main_sizer=wx.BoxSizer(wx.VERTICAL)
        
        axes=[]
        if main_frame.main_water_check.IsChecked():
            axes.append('W')
        elif main_frame.main_temp_check.IsChecked():
            axes.append('T')
        elif OP_p1_RPS and main_frame.main_turbo_pump_check.IsChecked():
            axes.append('P')
        elif OP_p1_VA and main_frame.main_turbo_pumpVA_check.IsChecked():
            axes.append('V')
        elif OP_top and OP_buffer and main_frame.main_cryo_pump_check.IsChecked():
            axes.append('C')
        
        if main_frame.water_check.IsChecked():
            axes.append('W')
        if main_frame.temp_check.IsChecked():
            axes.append('T')
        if OP_p1_RPS and main_frame.turbo_pump_check.IsChecked():
            axes.append('P')
        if (OP_p1_VA or OP_p2_VA) and main_frame.turbo_pumpVA_check.IsChecked():
            axes.append('V')
        if OP_top and OP_buffer and main_frame.cryo_pump_check.IsChecked():
            axes.append('C')
            
        if axes[-1]=='W':
            self.data_text="Time: %s, Water flow: %s"
        elif axes[-1]=='T':
            self.data_text="Time: %s, Water temperature: %s"
        elif axes[-1]=='P':
            self.data_text="Time: %s, Turbo pumps RPS: %s"
        elif axes[-1]=='V':
            self.data_text="Time: %s, Turbo pumps VA: %s"
        elif axes[-1]=='C':
            self.data_text="Time: %s, Cryo pumps temperature: %s"

        
        self.figure = Figure(figsize=(9, 4), dpi=80)
        self.figure.subplots_adjust(top=0.97)
        self.ax1 = self.figure.add_subplot(111)
        
        now=datetime.datetime.now()
        bottom_limit=datetime.date(now.year, now.month, now.day)
        upper_limit=datetime.date(now.year, now.month, now.day+1)
        
        if axes:
            for ax in axes:
                if ax=='W':
                    ax_min=min(OP_water)-1
                    ax_max=max(OP_water)+1
                    ax_ylabel='Water flow [l/min]'
                    y1_data=OP_water
                    line1='b-'
                    plot1_label="Water flow"
                    colour='b'
                    legend_loc=2
                elif ax=='T':
                    OP_T_sorted = set(filter(lambda x: x == x , OP_t1+OP_t2))
                    ax_min=(sorted(OP_T_sorted)[0])-1
                    ax_max=(sorted(OP_T_sorted)[-1])+1
                    ax_ylabel='Temperature [°C]'
                    y1_data=OP_t1
                    y2_data=OP_t2
                    line1='r-'
                    line2='g-'
                    plot1_label="Temperature In"
                    plot2_label="Temperature Out"
                    colour='g'
                    legend_loc=1
                    
                elif ax=='P':
                    if OP_p2_RPS:
                        OP_p_RPS_sorted = set(filter(lambda x: x == x , OP_p1_RPS+OP_p2_RPS))
                        ax_min=(sorted(OP_p_RPS_sorted)[0])-4
                        ax_max=(sorted(OP_p_RPS_sorted)[-1])+3
                    else:
                        OP_p_RPS_sorted = set(filter(lambda x: x == x , OP_p1_RPS))
                        ax_min=(sorted(OP_p_RPS_sorted)[0])-4
                        ax_max=(sorted(OP_p_RPS_sorted)[-1])+3
                    if ax_min>950: 
                        ax_min=ax_min-50
                        ax_max=ax_max+40
                    ax_ylabel='Turbo pump [RPS]'
                    y1_data=OP_p1_RPS
                    y2_data=OP_p2_RPS
                    line1='m-'
                    line2='k-'
                    plot1_label="LL pump"
                    plot2_label="PM pump"
                    colour='m'
                    legend_loc=4
                    
                elif ax=='V':
                    if OP_p2_VA:
                        OP_p_VA_sorted = set(filter(lambda x: x == x , OP_p1_VA+OP_p2_VA))
                        ax_min=(sorted(OP_p_VA_sorted)[0])-4
                        ax_max=(sorted(OP_p_VA_sorted)[-1])+3
                    else:
                        OP_p_VA_sorted = set(filter(lambda x: x == x , OP_p1_VA))
                        ax_min=(sorted(OP_p_VA_sorted)[0])-4
                        ax_max=(sorted(OP_p_VA_sorted)[-1])+3
                    ax_ylabel='Turbo pump [VA]'
                    y1_data=OP_p1_VA
                    y2_data=OP_p2_VA
                    line1='y-'
                    line2='r-'
                    plot1_label="LL pump VA"
                    plot2_label="PM pump VA"
                    colour='y'
                    legend_loc=8
                    
                elif ax=='C':
                    OP_C_combined=[]
                    if OP_top:
                        OP_C_combined+=OP_top
                    if OP_buffer:
                        OP_C_combined+=OP_buffer
                    if OP_side:
                        OP_C_combined+=OP_side
                    if OP_LL:
                        OP_C_combined+=OP_LL
                    OP_c_sorted = set(filter(lambda x: x == x , OP_C_combined))
                    ax_min=(sorted(OP_c_sorted)[0])-4
                    ax_max=(sorted(OP_c_sorted)[-1])+3
                    ax_ylabel='Cryo pumps [K]'
                    y1_data=OP_top
                    y2_data=OP_buffer
                    y3_data=OP_side
                    y4_data=OP_LL
                    line1='c-'
                    line2='k-'
                    line3='#380282'
                    line4='r-'
                    plot1_label="Top pump"
                    plot2_label="Buffer pump"
                    plot3_label='Side pump'
                    plot4_label='Load Lock pump'
                    colour='c'
                    legend_loc=3
                
                if ax==axes[0]:
                    self.ax1.set_ylim([ax_min,ax_max])
                    now=datetime.datetime.now()
                    self.ax1.set_xlim(bottom_limit,upper_limit)
                    self.ax1.set_xlabel('Time [hh:mm:ss]')
                    self.ax1.set_ylabel(ax_ylabel)
                    self.water_plot=self.ax1.plot(OP_time, y1_data, line1, linewidth=0.3, label=plot1_label)
                    self.ax1.yaxis.label.set_color(colour)
                    if ax=='T' or ax=='C' or (ax=='V' and OP_p2_VA):self.temp2_plot=self.ax1.plot(OP_time ,y2_data, line2, linewidth=0.3, label=plot2_label)
                    if ax=='C':
                        if OP_side: self.temp3_plot=self.ax1.plot(OP_time ,y3_data, line3, linewidth=0.3, label=plot3_label)
                        if OP_LL: self.temp4_plot=self.ax1.plot(OP_time, y4_data, line4, linewidth=0.3, label=plot4_label)
                    self.ax1.legend(loc=legend_loc)
                else:
                    new_plot=self.ax1.twinx()
                    new_plot.set_ylim([ax_min,ax_max])
                    new_plot.set_xlim(bottom_limit,upper_limit)
                    new_plot.set_ylabel(ax_ylabel)
                    self.temp1_plot=new_plot.plot(OP_time, y1_data, line1, linewidth=0.3, label=plot1_label)
                    if ax=='T' or ax=='C' or (ax=='V' and OP_p2_VA):self.temp2_plot=new_plot.plot(OP_time ,y2_data, line2, linewidth=0.3, label=plot2_label)
                    if ax=='C':
                        if OP_side: self.temp3_plot=new_plot.plot(OP_time ,y3_data, line3, linewidth=0.3, label=plot3_label)
                        if OP_LL: self.temp4_plot=new_plot.plot(OP_time, y4_data, line4, linewidth=0.3, label=plot4_label)
                    if ax=='P' and OP_p2_RPS: self.temp2_plot=new_plot.plot(OP_time ,y2_data, line2, linewidth=0.3, label=plot2_label)
                    new_plot.yaxis.label.set_color(colour)
                    new_plot.legend(loc=legend_loc)
                    if len(axes)>1:new_plot.spines['right'].set_position(('outward', (axes.index(ax)-1)*45))         
         
        self.canvas = FigureCanvas(self,-1, self.figure)
       
        self.ax1.set_xticklabels(OP_time,rotation=25)
        xfmt = md.DateFormatter('%H:%M:%S')
        self.ax1.xaxis.set_major_formatter(xfmt)       
        
        self.figure.tight_layout()
        
        
        self.chart_toolbar = NavigationToolbar2Wx(self.canvas)
        self.chart_toolbar.Realize()
        
        self.main_sizer.Add(self.chart_toolbar, flag=wx.EXPAND, border=5)
        self.main_sizer.Add(self.canvas)
        
        self.SetSizer(self.main_sizer)
        self.Layout()
        
        self.Bind(wx.EVT_CLOSE, self.CloseSelf)
        self.statusbar = self.CreateStatusBar()
        
        if main_frame.cursor_line.IsChecked():
            if len(axes)>1:
                self.cursor = Cursor(new_plot, useblit=True, color='black', linewidth=0.5)
            else:
                self.cursor = Cursor(self.ax1, useblit=True, color='black', linewidth=0.5)
    
        mouseMoveID = self.canvas.mpl_connect('motion_notify_event', self.onMotion)
        
        self.SetMinSize((735, 415))
        self.SetMaxSize((735, 415))

    def onMotion(self, evt):
        xdata = evt.xdata
        ydata = evt.ydata

        if xdata is not None and ydata is not None:
            ydata=round(ydata,2)
            frac, whole = math.modf(xdata)
            seconds=int(frac*3600*24)
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            xdata=datetime.time(hours, minutes, seconds)
        self.statusbar.SetStatusText(self.data_text % (xdata, ydata))

    def CloseSelf(self, event):
        global OP_time, OP_t1, OP_t2, OP_water, old_plot_window

        self.figure.clf()
        plt.close()
        gc.collect()
        self.Destroy()        

class info_window(wx.Dialog):
   
    def __init__(self, parent, title):
        super(info_window, self).__init__(parent, title=title, size=(400,300))
           
        self.InitUI()    
        self.Centre()
        self.Show()
         
    def InitUI(self):
        main_panel = wx.Panel(self)
        main_panel.SetBackgroundColour('#ededed')
        main_sizer = wx.BoxSizer(wx.VERTICAL)
         
        scroll_panel=scrolled.ScrolledPanel(main_panel, size=(350,320))
        scroll_panel.SetAutoLayout(1)
        scroll_panel.SetupScrolling(scroll_x=False)
        scroll_panel.SetBackgroundColour('#ededed')
        scroll_sizer=wx.BoxSizer(wx.VERTICAL)
        
        text_panel=wx.Panel(scroll_panel)
        
        infopath=os.path.join(data_path,'GW_info.txt')
        label=open(infopath, 'r').read()
        self.txt=wx.StaticText(text_panel, label=label, style=wx.ST_NO_AUTORESIZE | wx.ALIGN_LEFT)
        self.txt.SetSize((320,320))
        scroll_sizer.Add(text_panel)
        scroll_panel.SetSizer(scroll_sizer)
         
        main_sizer.Add(scroll_panel,flag=wx.ALL|wx.ALIGN_CENTER, border=10)   
       
        main_panel.SetSizer(main_sizer)


if __name__ == '__main__':
    
    app = wx.App()
    main_frame=main_window(None, title='PM graph viewer')
    app.MainLoop()