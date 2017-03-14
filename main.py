#!/usr/bin/python

"""
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2017/03/09 $"
"""

import warnings
import json
import os
import sys
import wx
from PythonCard import model, dialog
import edtask


def init_from_dict(D):
    '''
        Return a list with content of sorted dict keys
    '''
    L = []
    for i in sorted(D.keys()):
        L.append(D[i])
    return L


def find_data_file(filename):
    '''
        Return full path of filename, assuming filename is in application folder
    '''
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, filename)





class MyBackground(model.Background):

    def on_initialize(self, event):
        '''
            Init and load config
        '''
        self.configfile = "config.json"
        self.filename = None
        self.changedFlag = False
        self._loadConfig()
        me = self.components
        me.usedFileName.text = ""
        me.info.text = ""
        me.sliderTmr0.min = 0        
        me.sliderTmr0.max = 255
        self.d_cpufreq = {
            0.25:"250 KHz", 0.5:"500 KHz", 
            1:"1 MHz", 2:"2 Mhz", 4:"4 MHz", 8:"8 MHz",
            12:"12 MHz", 16:"16 MHz", 20:"20 MHz", 32:"32 MHz", 48:"48 MHz"}
        self.d_prescaler = {1:"1:1 - ps WDT",
            2:"1:2", 4:"1:4", 8:"1:8", 16:"1:16", 32:"1:32",
            64:"1:64", 128:"1:128", 256:"1:256"}
        me.cpufreq.items = init_from_dict(self.d_cpufreq)
        me.prescaler.items = init_from_dict(self.d_prescaler)
        #default selection
        me.picmodel.selection = 0
        me.cpufreq.selection = 4
        me.prescaler.selection = 2
        self.on_picmodel_select(None)
        self.on_inittmr0_textUpdate(None)
        self.task_list = []
        me.tasklist.columnHeadings = ("#", "#ms", "Task title", "Body")
        L = []
        for i, t in enumerate(self.task_list):
            l = [str(i), str(t['period']), t['name'], t['body']]
            L.append(l)
        me.tasklist.items = L
        self._format_tasklist()

    def on_close(self, event):
        '''
            Close application
        '''
        if self.changedFlag:
            result = dialog.messageDialog(self, 'Unsaved work.\nContinue?', 'Warning', wx.ICON_WARNING | wx.YES_NO)
            if not result.accepted:
                return
        self.Destroy()

    def _error(self, error, title):
        '''
            Generic error dialog
        '''
        dialog.messageDialog(self, str(error), title, wx.ICON_ERROR | wx.OK)

    def _loadConfig(self):
        '''
            Load and parse json config file
        '''
        filename = find_data_file(self.configfile)
        f = open(filename, "rt")
        self.config = json.loads(f.read())
        f.close()
        self.components.picmodel.items = self.config['global']['piclist']
        self.jalcompiler = self.config['global']['jalcompiler']
        self.jallibrary = self.config['global']['jallibrary']
        if not os.path.isfile(self.jalcompiler):
            self._error('JAL Compiler path is invalid', 'config global jallibrary')

    def on_picmodel_select(self, event):
        '''
            When pic model is changed,
            the initJALCode section is updated
        '''
        if self.changedFlag:
            result = dialog.messageDialog(self, 'Unsaved work.\nContinue?', 'Warning', wx.ICON_WARNING | wx.YES_NO)
            if not result.accepted:
                return
        me = self.components
        self.initJALCode = self.config.get(me.picmodel.items[me.picmodel.selection], '-- no init defined in config')
        self.changedFlag = False

    def on_cpufreq_select(self, event):
        '''
            When cpu freq is changed, update display info
        '''
        self.on_inittmr0_textUpdate(event)

    def on_prescaler_select(self, event):
        '''
            When prescaler is changed, update display info
        '''
        self.on_inittmr0_textUpdate(event)

    def on_cmdslider_command(self, event):
        '''
            When slider is changed, update display info
        '''
        me = self.components
        cpu_freq = sorted(self.d_cpufreq.keys())[me.cpufreq.selection]
        prescaler_ratio = sorted(self.d_prescaler.keys())[me.prescaler.selection]
        slidervalue = int(me.sliderTmr0.value)
        #slider update text
        me.inittmr0.text = str(slidervalue)
        period = (me.sliderTmr0.max+1 - slidervalue) * 4.0 * prescaler_ratio / cpu_freq #microseconds
        me.info.text = "Period: {:.2f} us = {:.2f} ms = {} s --- Freq: {:.2f} Hz = {:.1f} KHz ".format(period, period / 1e3, period / 1e6, 1e6 / period, 1e3 / period)

    def on_inittmr0_textUpdate(self, event):
        '''
            When TMR0 init value is changed, update display info
        '''
        me = self.components
        cpu_freq = sorted(self.d_cpufreq.keys())[me.cpufreq.selection]
        prescaler_ratio = sorted(self.d_prescaler.keys())[me.prescaler.selection]
        maxval = me.sliderTmr0.max
        try:
            initTMR0 = int(me.inittmr0.text)
        except:
            initTMR0 = 0
        if initTMR0 >= maxval: initTMR0 = maxval
        #text update slider
        me.sliderTmr0.value = int(initTMR0)
        period = (maxval+1 - initTMR0) * 4.0 * prescaler_ratio / cpu_freq #microseconds
        me.info.text = "Period: {:.2f} us = {:.2f} ms = {} s --- Freq: {:.2f} Hz = {:.1f} KHz ".format(period, period / 1e3, period / 1e6, 1e6 / period, 1e3 / period)

    def on_new_command(self, event):
        '''
            New project
        '''
        me = self.components
        if self.changedFlag:
            result = dialog.messageDialog(self, 'Unsaved work.\nContinue?', 'Warning', wx.ICON_WARNING | wx.YES_NO)
            if not result.accepted:
                return
        self.changedFlag = False
        self.filename = None
        me.usedFileName.text = "New config, default config"
        self.task_list = [
            {'name':'Task 1', 'period':1000.0, 'body':'asm nop\nasm nop'},
            ]
        self.initJALCode = self.config.get(me.picmodel.items[me.picmodel.selection], '-- no init defined')
        L = []
        for i, t in enumerate(self.task_list):
            l = [str(i), str(t['period']), t['name'], t['body']]
            L.append(l)
        me.tasklist.items = L
        self._format_tasklist()


    def on_saveas_command(self, event):
        self.filename = None
        self.on_save_command(event)

    def on_save_command(self, event):
        '''
            Save project in json format
        '''
        if not self.filename:
            result = dialog.saveFileDialog(self, 'Save', '', '', '*.json')
            if result.accepted:
                self.filename = result.paths[0]
                self.components.usedFileName.text = self.filename
        if self.filename:
            self.task_list = []
            for i in self.components.tasklist.items:
                d = {'name':i[2], 'period':float(i[1]), 'body':i[3]}
                self.task_list.append(d)
            d = {}
            me = self.components
            d['initJALCode'] = self.initJALCode
            d['task_list'] = self.task_list
            d['picmodel'] = me.picmodel.selection
            d['cpufreq'] = me.cpufreq.selection
            d['prescaler'] = me.prescaler.selection
            d['inittmr0'] = int(me.inittmr0.text)
            f = open(self.filename, "wt")
            f.write(json.dumps(d, sort_keys=True, indent=4, separators=(',', ': ')))
            f.close()
        self.changedFlag = False

    def on_load_command(self, event):
        '''
            Load project in json format
        '''
        try:
            if self.changedFlag:
                result = dialog.messageDialog(self, 'Unsaved work.\nContinue?', 'Warning', wx.ICON_WARNING | wx.YES_NO)
                if not result.accepted:
                    return
            result = dialog.openFileDialog(self, 'Load', '', '', '*.json')
            if result.accepted:
                self.filename = result.paths[0]
                self.components.usedFileName.text = self.filename
                f = open(self.filename, "rt")
                d = json.loads(f.read())
                f.close()
                me = self.components
                self.initJALCode = d['initJALCode']
                self.task_list = d['task_list']
                me.picmodel.selection = d['picmodel']
                me.cpufreq.selection = d['cpufreq']
                me.prescaler.selection = d['prescaler']
                me.inittmr0.text = str(d['inittmr0'])
                L = []
                for i, t in enumerate(self.task_list):
                    l = [str(i), str(t['period']), t['name'], t['body']]
                    L.append(l)
                self.components.tasklist.items = L
                self._format_tasklist()
            self.changedFlag = False
            self.on_inittmr0_textUpdate(None)
        except Exception as ex:
            self._error(ex, 'Error loading file')




    def _format_tasklist(self):
        '''
            Update task list
        '''
        me = self.components
        L = []
        for i, t in enumerate(me.tasklist.items):
            t[0] = str(i)
            L.append(t)
        me.tasklist.items = L
        me.tasklist.SetColumnWidth(0, 30)  #task position and order
        me.tasklist.SetColumnWidth(1, 70)  #scheduled rate in ms
        me.tasklist.SetColumnWidth(2, 120) #task title

    def _edit_TASK(self):
        '''

            Callback from edit dialog

        '''
        #index task
        ix = self.edtask.ix
        if ix < 0:
            #update init JAL code
            self.initJALCode = self.edtask.components.blockCode.text
            self.changedFlag = True
        else:
            #update Task
            try:
                try: sched_rate = float(self.edtask.components.schRate.text)
                except: sched_rate = 0
                L = self.components.tasklist.items
                L[ix][1] = str(sched_rate)
                L[ix][2] = self.edtask.components.taskName.text
                L[ix][3] = self.edtask.components.blockCode.text
                self.components.tasklist.items = L
                self._format_tasklist()
                self.changedFlag = True
            except Exception as ex:
                self._error(ex, 'Error edit task')



    def on_edinitconfig_command(self, event):
        '''
            Edit init code for selected processor
        '''
        self.edtask = model.childWindow(self, edtask.MyBackground)
        self.edtask.ix = -1
        self.edtask.callback = self._edit_TASK
        self.edtask.parent = self
        self.edtask.components.dialogTitle.text = "Edit init code"
        self.edtask.title = "Edit init code"
        self.edtask.components.taskName.visible = False
        self.edtask.components.schRate.visible = False
        self.edtask.components.StaticText3.visible = False
        self.edtask.components.StaticText1.visible = False
        self.edtask.components.blockCode.text = self.initJALCode
        self.edtask.components.blockCode.SetFocus()
        self.edtask.MakeModal(True)


    def on_tasklist_mouseDoubleClick(self, event):
        '''
            Edit task on mouse Double Click
        '''
        self.on_edittask_command(event)

    def on_edittask_command(self, event):
        '''
            Edit selected task
        '''
        if not self.components.tasklist.GetSelectedItems():
            return self._error('No task selected.', 'Error edit task')
        try:
            ix = int(self.components.tasklist.GetSelectedItems()[0][0])
            tl = self.components.tasklist.items[ix]
            self.edtask = model.childWindow(self, edtask.MyBackground)
            self.edtask.ix = ix
            self.edtask.callback = self._edit_TASK
            self.edtask.parent = self
            self.edtask.components.Button3.visible = False
            self.edtask.components.dialogTitle.text = "Edit task"
            self.edtask.title = "Edit task"
            self.edtask.components.taskName.text = tl[2]
            self.edtask.components.schRate.text = tl[1]
            self.edtask.components.blockCode.text = tl[3]
            self.edtask.components.blockCode.SetFocus()
            self.edtask.MakeModal(True)
            self._format_tasklist()
        except Exception as ex:
            self._error(ex, 'Error edit task')

    def on_inserttask_command(self, event):
        '''
            Add a task before selected task
        '''
        if not self.components.tasklist.items:
            l = ['', '1000', 'New Task', 'asm nop']
            self.components.tasklist.items = [l]
            self.changedFlag = True
        else:
            if not self.components.tasklist.GetSelectedItems():
                return self._error('No place selected to insert before.', 'Error insert task')
            try:
                L = []
                ix = int(self.components.tasklist.GetSelectedItems()[0][0])
                for i in self.components.tasklist.items[:ix]:
                    L.append(i)
                l = ['', '1000.0', 'New Task', 'asm nop']
                L.append(l)
                for i in self.components.tasklist.items[ix:]:
                    L.append(i)
                self.components.tasklist.items = L
                self.changedFlag = True
            except Exception as ex:
                #print ex
                self._error(ex, 'Error insert task')
        self._format_tasklist()

    def on_deletetask_command(self, event):
        '''
            Delete selected task
        '''
        if not self.components.tasklist.GetSelectedItems():
            return self._error('No task selected.', 'Error delete task')
        try:
            L = []
            ix = int(self.components.tasklist.GetSelectedItems()[0][0])
            result = dialog.messageDialog(self, 'Delete selected task?\n\n', 'Warning', wx.ICON_WARNING | wx.YES_NO)
            if not result.accepted:
                return
            for i in self.components.tasklist.items:
                if ix != int(i[0]):
                    L.append(i)
            self.components.tasklist.items = L
            self._format_tasklist()
            self.changedFlag = True
        except Exception as ex:
            self._error(ex, 'Error delete task')

    def on_moveup_command(self, event):
        '''
            Move up selected task
        '''
        try:
            ix = int(self.components.tasklist.GetSelectedItems()[0][0])
            if ix > 0:
                L = self.components.tasklist.items
                a = L[ix]
                b = L[ix-1]
                L[ix] = b
                L[ix-1] = a
                self.components.tasklist.items = L
                self._format_tasklist()
                self.changedFlag = True
        except Exception as ex:
            #ignore error
            pass

    def on_movedown_command(self, event):
        '''
            Move down selected task
        '''
        try:
            ix = int(self.components.tasklist.GetSelectedItems()[0][0])
            if ix < len(self.components.tasklist.items):
                L = self.components.tasklist.items
                a = L[ix]
                b = L[ix+1]
                L[ix] = b
                L[ix+1] = a
                self.components.tasklist.items = L
                self._format_tasklist()
                self.changedFlag = True
        except Exception as ex:
            #ignore error
            pass

    def on_generate_command(self, event):
        '''
            Generate JAL file
        '''
        if not os.path.isfile(self.jalcompiler):
            self._error('JAL Compiler path is invalid', 'config global jallibrary')
        outfile = self.config['global']['generated_file']
        errfile = self.config['global']['compiler_message_file']
        me = self.components
        self.task_list = []
        me.inittmr0.text = str(me.sliderTmr0.value) #force generate with slider value
        for i in me.tasklist.items:
            d = {'name':i[2], 'period':float(i[1]), 'body':i[3]}
            self.task_list.append(d)
        cpu_freq = sorted(self.d_cpufreq.keys())[me.cpufreq.selection]
        prescaler_ratio = sorted(self.d_prescaler.keys())[me.prescaler.selection]
        pic_model = me.picmodel.items[me.picmodel.selection]
        maxval = me.sliderTmr0.max
        try: initTMR0 = int(me.inittmr0.text)
        except: initTMR0 = 0
        period = (1 + maxval - initTMR0) * 4.0 * prescaler_ratio / cpu_freq #microseconds
        if prescaler_ratio == 1:
            set_prescaler = "OPTION_REG_PSA = 1  -- Prescaler is assigned to WDT"
        else:
            ps_bits = {2:'000', 4:'001', 8:'010', 16:'011', 32:'100', 64:'101', 128:'110', 256:'111'}
            bits = ps_bits[prescaler_ratio]
            set_prescaler = '''OPTION_REG_PSA = 0  -- Prescaler is assigned to the Timer0 module
;set prescaler for 1:{}
OPTION_REG_PS0 = {}
OPTION_REG_PS1 = {}
OPTION_REG_PS2 = {}
'''.format(prescaler_ratio, bits[2], bits[1], bits[0])
        outCode = '''
pragma target clock {0} -- oscillator frequency
include {1}

; assume serial bootloader from
; http://www.etc.ugal.ro/cchiculita/software/picbootloader.htm
pragma fuses NO

{2}

-- task scheduler counters
'''.format(int(cpu_freq * 1e6), pic_model, self.initJALCode)
        #generate task counters
        period_ms = period / 1e3
        for i, t in enumerate(self.task_list):
            if t['period']:
                #task_counter_limit = scheduled_rate_ms / period_ms
                task_counter_limit = float(t['period'] / period_ms)
                if task_counter_limit < 1:
                    msg = 'Error: "{}" has scheduled period too short: {:.2f} ms.'.format(t['name'], t['period'])
                    return self._error(msg, 'Generate')
                if task_counter_limit < 255:
                    #use byte
                    outCode += "var volatile byte cnt_task_{} = 0\n".format(i)
                else:
                    if task_counter_limit < 65535:
                        #use word
                        outCode += "var volatile word cnt_task_{} = 0\n".format(i)
                    else:
                        #use dword
                        outCode += "var volatile dword cnt_task_{} = 0\n".format(i)

        outCode += '''
-- Init TMR0, set prescaler, enable interrupts
TMR0 = {}
OPTION_REG = 0
{}
OPTION_REG_T0CS = 0 -- Internal instruction cycle clock (CLKO)
INTCON = 0
INTCON_TMR0IE = 1
INTCON_GIE = 1

-- main loop starts here
forever loop
'''.format(initTMR0, set_prescaler)

        #task list in mainloop
        for i, t in enumerate(self.task_list):
            #format body
            task_counter_limit = float(t['period'] / period_ms)
            body = ""
            for line in t['body'].split("\n"):
                if t['period'] == 0:
                    s = " "*4 + line + "\n"
                else:
                    s = " "*8 + line + "\n"
                body += s
            body = body[:-1]
            if t['period'] == 0:
                outCode += '''
    -- "{0}" run each cycle
{1}
    -- end {0}
'''.format(t['name'], body)
            else:
                outCode += '''
    -- "{0}" run each {1} ms, maxcount = {1} ms / {2:.2f} ms = {4:.2f}
    if cnt_task_{3} > {4:.0f} then
        cnt_task_{3} = 0
{5}
    end if
    -- end {0}
'''.format(t['name'], t['period'], period_ms, i, task_counter_limit, body)
        outCode += '''
-- end main loop
end loop


'''

        #ISR TMR0
        outCode += '''
-- Interrupt TMR0 period: {:.2f} us = {:.2f} ms = {:.2f}s, Frequency: {:.2f} Hz
procedure TMR0_interrupt_handler() is
    pragma interrupt normal

    if INTCON_TMR0IF == True then
       -- TMR0 overflow
       TMR0 = {}
       INTCON_TMR0IF = False

       -- update task counters
'''.format(period, period / 1e3, period / 1e6, 1e6 / period, initTMR0)
        for i, t in enumerate(self.task_list):
            if t['period']:
                outCode += '''      cnt_task_{0} = cnt_task_{0} + 1
'''.format(i)
        outCode += '''   end if

end procedure



;end program


'''
        f = open(outfile, "wt")
        f.write(outCode)
        f.close()
        cmd = "{} -s .;{} {} > {}".format(self.jalcompiler, self.jallibrary, outfile, errfile)
        ret = os.system(cmd)
        f = open(errfile, 'rt')
        outerrmsg = f.read(1500)
        f.close()
        if ret:
            flags = wx.ICON_ERROR | wx.OK
        else:
            flags = wx.ICON_INFORMATION | wx.OK
        if outerrmsg:
            dialog.messageDialog(self, outerrmsg, 'Compile', flags)

    def on_about_command(self, event):
        result = dialog.messageDialog(self, '''JAL Code Generator

(C) 2017 Ioan Coman
http://rainbowheart.ro/

wx version: {}

Python version:
{}

'''.format(wx.version(), sys.version), 'About', wx.ICON_INFORMATION | wx.OK) #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL)


def fix_frozen_apps():
    #
    #fix import for py2exe, cx_freeze, pyinstaller, ...
    #
    #import here whatever fail to import when application is frozen
    #
    #import pyodbc, pymssql, _mssql
    from PythonCard.components import slider
    #from PythonCard.components import radiogroup
    from PythonCard.components import button
    #from PythonCard.components import list
    from PythonCard.components import choice
    from PythonCard.components import statictext
    #from PythonCard.components import checkbox
    #from PythonCard.components import gauge
    from PythonCard.components import multicolumnlist
    #from PythonCard.components import passwordfield
    from PythonCard.components import textarea
    from PythonCard.components import combobox
    #from PythonCard.components import calendar



if __name__ == '__main__':
    warnings.simplefilter("ignore")
    app = model.Application(MyBackground)
    app.MainLoop()
