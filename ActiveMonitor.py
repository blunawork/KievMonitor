import re
import json 
import requests

from kivy.app            import App
from kivy.lang           import Builder
from functools           import partial
from kivy.clock          import Clock
from kivy.config         import Config
from kivy.uix.gridlayout import GridLayout

json_data = '{}'

# A set size main window.
Config.set( 'graphics', 'resizable', False )

def net_fetch( dt ): 

	global json_data

	r      = requests.get( 'http://central-server.example.com' )
	status = r.status_code
	
	if ( status == 200 ): 
		json_data = str( json.dumps( r.json() ) )
		json_data = json.loads( json_data )

		print(json_data)
	
net_fetch( 60 )

# Loop for 60 seconds.
Clock.schedule_interval( net_fetch, 60 )

btn_bg_hl    = (0, 0, 1, .5);
btn_bg_in    = (0, 0, 0, 1);
sorted_hosts = sorted( list( json_data.keys() ) )
first_host   = sorted_hosts[0]

# Color ranges.
color_map = {
	tuple( range(0, 26)  ) : (0, 0, 1, .5), # Blue
	tuple( range(26, 51) ) : (0, 1, 0, .5), # Green
	tuple( range(51, 76) ) : (1, 1, 0, .5), # Yellow
	76                     : (1, 0, 0, .5), # Red
}

# Just return the color in the color map.
def set_level_color( **kwargs ):

	percent = kwargs.get('percent')

	# Clear out funky chars.
	percent = str( percent )
	percent = re.sub( r'^0|%$', '', percent )
	percent = re.sub( r'\..*',  '', percent )
	percent = percent if percent else 1
	percent = int( percent )

	# Return.
	result = ()
	
	for m in ( color_map ):  
	
		# Either tuple or int.
		if ( isinstance( m, tuple ) ):
			if ( percent in m ):
				result = color_map[ m ]
				break;
		else: 
			result = color_map[ m ]
			break;
	
	return result

# Buttons.
def make_host_buttons( **kwargs ): 

	json_data = kwargs.get('json_data')

	count     = 0
	kv_string = ''

	# Defaults.
	host_btn_border = (163/255, 169/255, 244/255, .5)
	host_btn_width  = 1.25

	for host in ( sorted_hosts ):

		# Fetch the greatest number to indicate the threat level.
		data = json_data.get( host )
		data = dict( sorted( data.items() ) )

		# Lookup threat level for the host.
		#num  = data[ max( data, key=data.get ) ]
		num   = data.get('disk')
		color = set_level_color( percent=num )

		bold     = False
		bg_color = btn_bg_in

		# Bold the first host button.
		if ( count == 0 ):
			bold     = True
			bg_color = btn_bg_hl

		kv_string += f'''
			Button:
				bold: {bold}
				id: btn{host}
				text: '{host}'
				color: {color}
				on_press: root.button_host( host='{host}' )
				background_color: {bg_color}
				canvas.before:
					Color:
						rgba: {host_btn_border}
					Line:
						rectangle: self.x, self.y, self.width, self.height
						width: {host_btn_width}
		'''
		
		count += 1

	return kv_string

# Rectangle colors.
cpu_color  = set_level_color( percent=json_data.get( first_host ).get( 'cpu'  ) )
disk_color = set_level_color( percent=json_data.get( first_host ).get( 'disk' ) )
mem_color  = set_level_color( percent=json_data.get( first_host ).get( 'mem'  ) )
swap_color = set_level_color( percent=json_data.get( first_host ).get( 'swap' ) )

title_text = first_host.upper()

kv_string = f'''
#:import hex kivy.utils.get_color_from_hex

<MyGridLayout>:
	rows: 2
	label_percent_x: 440
	label_percent_y: 95
	rec_pos_x: 450
	rec_pos_y: 122
	rec_text_x: 250
	rec_text_y: 95
	title_text: "{title_text}"
	cpu: {json_data.get( first_host ).get( 'cpu' )}
	disk: {json_data.get( first_host ).get( 'disk' )}
	mem: {json_data.get( first_host ).get( 'mem' )}
	swap: {json_data.get( first_host ).get( 'swap' )}
	FloatLayout:
		Label:
			markup: True
			id: title
			font_size: 25
			text: root.title_text
			pos: (0,280)
			bold: True
		Widget: 
			canvas:
				Color:
					rgba: hex('#A3A9F4')
				Line:
					id: vert_1
					points: 400, 500, 400, 120
					width: 1
				Line:
					id: horz_1
					points: 600, 400, 200, 400 
					width: 1
				Line:
					id: horz_2
					points: 600, 300, 200, 300
					width: 1
				Line:
					id: horz_3
					points: 600, 200, 200, 200
					width: 1
		Widget: 
			id: rec_cpu
			color: {cpu_color}
			canvas:
				Color:
					rgba: self.color
				Rectangle: 
					pos: (root.rec_pos_x, root.rec_pos_y)
					size: (75, 50)
		Widget: 
			id: rec_disk
			color: {disk_color}
			canvas:
				Color:
					rgba: self.color
				Rectangle: 
					pos: (root.rec_pos_x, root.rec_pos_y + 100)
					size: (75, 50)
		Widget: 
			id: rec_mem
			color: {mem_color}
			canvas:
				Color:
					rgba: self.color
				Rectangle: 
					pos: (root.rec_pos_x, root.rec_pos_y + 200)
					size: (75, 50)
		Widget: 
			id: rec_swap
			color: {swap_color}
			canvas:
				Color:
					rgba: self.color
				Rectangle: 
					pos: (root.rec_pos_x, root.rec_pos_y + 300)
					size: (75, 50)
		Widget: 
			id: percents
			cpu  : str( root.cpu  ) + "%"
			disk : str( root.disk ) + "%"
			mem  : str( root.mem  ) + "%"
			swap : str( root.swap ) + "%"
			Label:
				text: percents.cpu
				pos: (root.label_percent_x, root.label_percent_y)
			Label:
				text: percents.disk
				pos: (root.label_percent_x, root.label_percent_y + 100)
			Label:
				text: percents.mem
				pos: (root.label_percent_x, root.label_percent_y + 200)
			Label:
				text: percents.swap
				pos: (root.label_percent_x, root.label_percent_y + 300)
		Widget: 
			Label:
				text: "CPU"
				pos: (root.rec_text_x, root.rec_text_y)
			Label: 
				text: "Disk"
				pos: (root.rec_text_x, root.rec_text_y + 100)
			Label: 
				text: "Memory"
				pos: (root.rec_text_x, root.rec_text_y + 200)
			Label: 
				text: "Swap"
				pos: (root.rec_text_x, root.rec_text_y + 300)
	BoxLayout:
		orientation: 'vertical'
		size_hint: 8, .1
		BoxLayout:
			height: 50
'''

kv_string += make_host_buttons( json_data=json_data )

Builder.load_string( kv_string )

class MyGridLayout( GridLayout ): 

	def __init__( self, **kwargs ):
		self.selected_host = None
		super( MyGridLayout, self ).__init__( **kwargs )

	def button_host( self, **kwargs ):
		
		host = kwargs.get( 'host' )

		# Current selected.
		if host is None: 
			host = self.selected_host

		# Perform the redraw.
		if host is not None: 

			self.selected_host = host
			
			# Parent window ids.
			ids = self.parent.children[0].ids
			
			# Set the title of the window to what was clicked.
			ids.title.text = host.upper()
			
			# Set all buttons to normal.
			for h in ( sorted_hosts ): 
				exec( f"ids.btn{h}.background_color={btn_bg_in}" )
				exec( f"ids.btn{h}.bold=False" )

				# Redraw all host percents, bottom buttons horz-nav. 
				data  = json_data.get( h )
				num   = data.get('disk')
				color = set_level_color( percent=num )
				exec( f"ids.btn{h}.color={color}" )
			
			# Rectangle color (selected button hl).
			exec( f"ids.btn{host}.background_color={btn_bg_hl}" )
			exec( f"ids.btn{host}.bold=True" )
			
			data = json_data.get( host )
			data = dict( sorted( data.items() ) )
			
			# Redraw percents and colors in each rectangle.
			for name in ( data ): 
				percent     = data[ name ]
				percent_mod = f"ids.percents.{name}"
				name        = f"ids.rec_{name}.color"
			
				# A string that becomes a ref.
				id_ref = str( name )
			
				# Make a ref out of id_ref and assign the new value.
				exec( f"{id_ref}=set_level_color( percent={percent} )" )
			
				# Change the percent value.
				exec( f"{percent_mod}='{percent}%'" )

class ActiveMonitorApp( App ): 

	def build( self ): 
		obj = MyGridLayout()
		Clock.schedule_interval( lambda *args: obj.button_host(host=None), 61 )
		return obj

if __name__ == "__main__":
	ActiveMonitorApp().run()
