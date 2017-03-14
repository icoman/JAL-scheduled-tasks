{'application':{'type':'Application',
          'name':'Template',
    'backgrounds': [
    {'type':'Background',
          'name':'bgTemplate',
          'title':'Standard Template with no menus',
          'size':(667, 471),

         'components': [

{'type':'Button', 
    'name':'Button3', 
    'position':(410, 90), 
    'size':(88, -1), 
    'command':u'updateconfig', 
    'label':u'Update config', 
    'toolTip':u'Update json config initJALCode for current processor with this code', 
    },

{'type':'TextField', 
    'name':'taskName', 
    'position':(90, 60), 
    'size':(170, -1), 
    },

{'type':'StaticText', 
    'name':'StaticText3', 
    'position':(20, 60), 
    'text':u'Task name:', 
    },

{'type':'TextArea', 
    'name':'blockCode', 
    'position':(10, 130), 
    'size':(620, 260), 
    },

{'type':'StaticText', 
    'name':'StaticText2', 
    'position':(50, 90), 
    'font':{'faceName': u'Segoe UI', 'family': 'sansSerif', 'size': 16}, 
    'text':u'JAL Code:', 
    },

{'type':'TextField', 
    'name':'schRate', 
    'position':(420, 60), 
    'size':(60, -1), 
    'text':u'1000', 
    },

{'type':'StaticText', 
    'name':'StaticText1', 
    'position':(280, 60), 
    'size':(128, -1), 
    'alignment':u'right', 
    'text':u'Scheduled rate [ms]:', 
    },

{'type':'StaticText', 
    'name':'dialogTitle', 
    'position':(50, 20), 
    'font':{'faceName': u'Segoe UI', 'family': 'sansSerif', 'size': 18}, 
    'text':u'StaticText1', 
    },

{'type':'Button', 
    'name':'Button2', 
    'position':(530, 90), 
    'command':u'cancel', 
    'label':u'Cancel', 
    },

{'type':'Button', 
    'name':'Button1', 
    'position':(530, 50), 
    'command':u'ok', 
    'label':u'Ok', 
    },

] # end components
} # end background
] # end backgrounds
} }
