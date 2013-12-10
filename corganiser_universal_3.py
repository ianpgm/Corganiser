import math
import collections
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

completed_requests = set()
previous_sample = ['empty','empty']

def core_mod(x,y):
	n = math.floor((x+0.01)/y)
	return(abs(n*y-x))



print("Content-type:text/html\r\n\r\n")
print("<HTML><HEAD><TITLE>Corganiser New .cor File</TITLE></HEAD><BODY><H1>Generating corganiser (.cor) file and resulting PDF...</H1>\n")

def placeWRC(width, depth,sampleID, last_sample):
	print("Placing " + sampleID + " at a target depth of " + str(depth) + "m (true depth " + str(starting_depth + depth/correction_factor) + "m)<br>")
	for core in core_depth_dict:
		if depth > hole_depth or depth < 0:
			print("Error! Sample outside of hole's depth range: " + sampleID + "<br>")
			exit()
		if sampleID in completed_requests:
			continue
		if depth >= core_depth_dict[core][0] - 0.01 and depth <= core_depth_dict[core][1] + 0.01:
			depth_section_base_diff = section_length
			for i in range(0,sections_per_core):
				section_base = core_depth_dict[core][0] + (i + 1) * section_length
				if abs(depth - section_base) < depth_section_base_diff:
					target_section = i
			if target_section+1 == sections_per_core and interval > section_length:
				target_section = target_section - 1
			highest_upper_sample = section_length
			lowest_lower_sample = 0
			
			upper_section_list = list()
			sorted_upper_section_list = list()
			
			for WRC in core_dict[core][target_section]:
				upper_section_list.append((core_dict[core][target_section][WRC][0],core_dict[core][target_section][WRC][1]))
			
			sorted_upper_section_list = sorted(upper_section_list, key=lambda upper_depth: upper_depth[0])
			
			if len(sorted_upper_section_list) == 0 or sorted_upper_section_list[-1][1] != 1.5:
				highest_upper_sample = 1.5
			else:
				if len(sorted_upper_section_list) == 1 or sorted_upper_section_list[0][0] != 0:
					highest_upper_sample = sorted_upper_section_list[0][0]
				else:	
					for WRC_depth in range(len(sorted_upper_section_list)):
						if sorted_upper_section_list[WRC_depth][1] == sorted_upper_section_list[WRC_depth+1][0]:
							continue
						else:
							highest_upper_sample = sorted_upper_section_list[WRC_depth+1][0]
							break
							
			if target_section+1 != sections_per_core:
				lower_section_list = list()
				sorted_lower_section_list = list()

				for WRC in core_dict[core][target_section+1]:
					lower_section_list.append((core_dict[core][target_section+1][WRC][0],core_dict[core][target_section+1][WRC][1]))

				sorted_lower_section_list = sorted(lower_section_list, key=lambda upper_depth: upper_depth[0])
				
				if len(sorted_lower_section_list) == 0 or sorted_lower_section_list[0][0] != 0:
					lowest_lower_sample = 0
				else:
					if sorted_lower_section_list[-1][1] != 1.5:
						lowest_lower_sample = sorted_lower_section_list[-1][1]
					else:	
						for WRC_depth in range(len(sorted_lower_section_list)):
							if sorted_lower_section_list[WRC_depth][1] == sorted_lower_section_list[WRC_depth+1][0]:
								continue
							else:
								lowest_lower_sample = sorted_lower_section_list[WRC_depth][1]
								break
			if last_sample[0] == sampleID.split(" ")[0]:
				if last_sample[1] == 'lower':
					core_dict[core][target_section+1][sampleID] = [lowest_lower_sample, lowest_lower_sample + width]
					print(sampleID + " placed in " + core + ", section " + str(target_section+2) + "<br>")
					return([request_number,'lower'])
				if last_sample[1] == 'upper':
					core_dict[core][target_section][sampleID] = [highest_upper_sample - width, highest_upper_sample]
					print(sampleID + " placed in " + core + ", section " + str(target_section+1) + "<br>")
					return([request_number,'upper'])
			else:
				if target_section+1 != sections_per_core and interval > section_length:
					core_dict[core][target_section+1][sampleID] = [lowest_lower_sample, lowest_lower_sample + width]
					print(sampleID + " placed in " + core + ", section " + str(target_section+2) + "<br>")
					return([request_number,'lower'])
				else:
					core_dict[core][target_section][sampleID] = [highest_upper_sample - width, highest_upper_sample]
					print(sampleID + " placed in " + core + ", section " + str(target_section+1) + "<br>")
					return([request_number,'upper'])
			completed_requests.add(sampleID)
	
colour_dict = dict()
name_dict = dict()

for line in open(sys.argv[1]):
	if line.startswith("hole_name"):
		hole_name = line.split("=")[1].split("\"")[1].strip(" \n\"")
	if line.startswith("core_length"):
		core_length = float(line.split("=")[1].strip(" \n"))	
	if line.startswith("unsampled_length"):
		unsampled_length = float(line.split("=")[1].strip(" \n"))	
	if line.startswith("hole_depth"):
		full_depth = float(line.split("=")[1].strip(" \n"))
	if line.startswith("sections_per_core"):
		sections_per_core = int(line.split("=")[1].strip(" \n"))
	if line.startswith("starting_depth"):
		starting_depth = float(line.split("=")[1].strip(" \n"))
	if line.startswith("starting_core"):
		starting_core = int(line.split("=")[1].strip(" \n"))
	if line.startswith("Begin Requests:"):
		correction_factor = core_length/(core_length + unsampled_length)
		hole_depth = (full_depth-starting_depth)*correction_factor
		core_dict = collections.OrderedDict()
		core_depth_dict = collections.OrderedDict()
		number_of_cores = int(hole_depth / core_length)
		number_of_sections = int(hole_depth / core_length) * sections_per_core
		section_length = float(core_length) / float(sections_per_core)
		print(str(hole_depth))
		print(str(core_length))
		print(str(core_mod(hole_depth,core_length)))
		if core_mod(hole_depth,core_length) > 0.01:
			print("Error! Hole depth must be a multiple of core length plus unsampled length.<br>")
			exit()
		else:
			for i in range(0, number_of_cores):
				top_of_core =  i * core_length
				base_of_core = i * core_length + core_length
				core_dict["core_" + str(i)] = list()
				core_depth_dict["core_" + str(i)] = [top_of_core,base_of_core]
				for j in range(0, sections_per_core):
					core_dict["core_" + str(i)].append(dict())
		print("Creating hole " + hole_name + " with depth range " + str(starting_depth) + "m to " + str(full_depth) + "m, core length " + str(core_length) + "m, " + str(sections_per_core) + " sections per core, and " + str(unsampled_length) + "m unsampled depth in between cores. Starting core numbering at " + str(starting_core) + ".<br>" )
	if line.startswith("request"):
		interval = section_length + 1
		request_number = line.split(" ")[1].split(":")[0]
		request_name = line.split(":")[1].strip("\" \n")
		name_dict[request_number] = request_name
		request_colour = line.split(":")[2].strip("\" \n")
		colour_dict[request_number] = request_colour
	if line.startswith('\"'):
		former_sample = ['0','0']
		request_label = line.split('\"')[1]
		if "WRC" in request_label:
			WRC_width = float(request_label.split(" ")[0].strip("cm")) / 100
			if "at" in line.split("\"")[2]:
				WRC_depth = float(line.split("\"")[2].split("at")[1].strip(" "))
				adjusted_depth = WRC_depth - starting_depth - WRC_depth*unsampled_length/core_length
				previous_sample = placeWRC(WRC_width,adjusted_depth,sampleID = request_number + " " + request_label + " " + str(WRC_depth), last_sample = former_sample)
				former_sample = previous_sample
			if "every" in line.split("\"")[2]:
				interval = float(line.split("\"")[2].split("every")[1].split("from")[0].strip(" "))
				if line.split("from")[1].split("to")[0].strip(" ") == "beginning":
					start_depth = 0
				else:
					start_depth = (float(line.split("from")[1].split("to")[0].strip(" ")) - starting_depth)*correction_factor
				if line.split("to")[1].strip(" \n") == "end":
					stop_depth = hole_depth
				else:
					stop_depth = (float(line.split("to")[1].strip(" \n")) - starting_depth)*correction_factor
				no_of_depths = int((stop_depth-start_depth)/interval)
				depth_list = list()
				for depth_number in range(1,no_of_depths+1):
					depth_list.append(start_depth+depth_number*interval)
				for depth in depth_list:
					previous_sample = placeWRC(WRC_width,depth,sampleID = request_number + " " + request_label + " " + str(depth), last_sample = former_sample)
				former_sample = previous_sample

def draw_short_cores():
	section_height_on_page = float(25 - sections_per_core) / float(sections_per_core)
	c = canvas.Canvas(sys.argv[1] + ".pdf")

	for core in core_dict:
		label_dict = dict()
		section_counter = 0
		print("creating sheet for " + core + "<br>")
		core_number = int(core.split("_")[1])
		c.setFont("Helvetica-Bold", 30)
		c.drawString(7*cm, 27.5*cm, "Core " + str(starting_core + core_number))
		c.drawString(7*cm, 26.5*cm, hole_name + ": " + str(float(starting_depth + core_depth_dict[core][0] + float(core_number)*unsampled_length)) + "m - " + str(float(starting_depth + core_depth_dict[core][1] + float(core_number+1)*unsampled_length)) + "m")
#		c.drawString(8*cm, 26.5*cm, hole_name + ": " + str(core_depth_dict[core][0]) + "m - " + str(core_depth_dict[core][1]) + "m")
		
		c.setFont("Helvetica", 10)
		c.drawString(4.1*cm, 28.1*cm, "TOP")
		c.drawString(3.7*cm, 3.5*cm, "BOTTOM")	
		section_counter = 0
		c.setFillColor('white')
		for section in core_dict[core]:
			start_point = 28-(section_counter+1)*section_height_on_page - section_counter
			c.rect(3*cm,start_point*cm,3*cm,section_height_on_page*cm, fill=0)
			c.line(2.8*cm,start_point*cm,2.8*cm,(start_point+section_height_on_page)*cm)
			c.rotate(90)
			c.setFillColor('black')
			c.setFont("Helvetica", 10)
			c.drawString((start_point+(1.3*section_height_on_page/3))*cm, -1.5*cm, "SECTION " + str(section_counter +1))
			c.rotate(-90)
			fivecm_notch_interval = int((section_length / 0.05)) + 1
			fivecm_notch_level = start_point
			for i in range(fivecm_notch_interval):
				fivecm_notch_level = start_point+i*section_height_on_page *(0.05 / section_length)
				c.line(2.8*cm,fivecm_notch_level*cm,2.6*cm,fivecm_notch_level*cm)
			twentyfivecm_notch_interval = int((section_length / 0.25)) + 1
			twentyfivecm_notch_level = start_point
			for i in range(twentyfivecm_notch_interval):
				twentyfivecm_notch_level = start_point+i*section_height_on_page *(0.25 / section_length)
				c.line(2.8*cm,twentyfivecm_notch_level*cm,2.4*cm,twentyfivecm_notch_level*cm)
				interval_name = section_length - 0.25*i
				c.setFont("Helvetica", 8)
				c.setFillColor('black')
				c.drawString(1.8*cm, (twentyfivecm_notch_level-0.1)*cm, str(int(100*interval_name)))
		
			for WRC in section:
				request_number = WRC.split(" ")[0]
				if request_number not in label_dict.keys():
					label_dict[request_number] = list()
				upper_limit = start_point + section_height_on_page *(1- section[WRC][0] / section_length)
				lower_limit = start_point + section_height_on_page *(1- section[WRC][1] / section_length)
				c.setFillColor(colour_dict[request_number])
				c.rect(3*cm,lower_limit*cm,3*cm,(upper_limit - lower_limit)*cm, fill=1)
				c.setFillColor('black')
				c.setFont("Helvetica", 8)
				c.drawString(4.1*cm, ((lower_limit+upper_limit)/2-0.1)*cm, request_number)
				descriptor = (WRC.split(" ")[1] + WRC.split(">")[1])
				descriptor_stripped = str()
				for word in descriptor.split(" ")[:len(descriptor.split(" "))-1]:
					descriptor_stripped = descriptor_stripped + " " + word
				c.drawString(6.1*cm, ((lower_limit+upper_limit)/2-0.1)*cm, descriptor_stripped)
#				c.drawString(6.1*cm, ((lower_limit+upper_limit)/2-0.1)*cm, descriptor)
			section_counter = section_counter + 1
			label_counter = 0
			for request_number in label_dict:
				box_height = 0.5
				start_point = (26 - 0.5*label_counter - box_height)
				c.setFillColor(colour_dict[request_number])
				c.rect(12*cm,(start_point-0.1)*cm,8*cm,(box_height)*cm, fill=1)
				c.setFont("Helvetica", 12)
				c.setFillColor('black')
				c.drawString(12.1*cm, (start_point+box_height-0.5)*cm, request_number + " " + name_dict[request_number])
				label_start_point = start_point+box_height-1
				label_counter = label_counter + 1.5
	
		c.showPage()

	c.save()

def draw_long_cores():
	section_height_on_page = 8
	c = canvas.Canvas(sys.argv[1] + ".pdf")	
	pages_per_core = sections_per_core / 3
	print(str(pages_per_core) + "<br>")
	
	for core in core_dict:
	
		for page in range(1,pages_per_core+1):
			label_dict = dict()	
			print("Creating sheet for " + core + "<br>")
			core_number = int(core.split("_")[1])
			c.setFont("Helvetica-Bold", 30)
			c.drawString(8*cm, 27.5*cm, "Core " + str(starting_core + core_number) + ", sections " + str(3*page-2) + "-" + str(3*page))
			c.drawString(8*cm, 26.5*cm, hole_name + ": " + str(float(starting_depth + core_depth_dict[core][0] + float(core_number)*unsampled_length)) + "m - " + str(float(starting_depth + core_depth_dict[core][1] + float(core_number+1)*unsampled_length)) + "m")
			c.setFont("Helvetica", 10)
			c.drawString(4.1*cm, 28.1*cm, "TOP")
			c.drawString(3.7*cm, 1.5*cm, "BOTTOM")	
			section_counter = 0
			c.setFillColor('white')
			for section in core_dict[core][3*page-3:3*page]:
				print("section counter " + str(section_counter) + "<br>")
				start_point = 28-(section_counter+1)*section_height_on_page - section_counter
				c.rect(3*cm,start_point*cm,3*cm,section_height_on_page*cm, fill=0)
				c.line(2.8*cm,start_point*cm,2.8*cm,(start_point+section_height_on_page)*cm)
				c.rotate(90)
				c.setFillColor('black')
				c.setFont("Helvetica", 10)
				c.drawString((start_point+(1.3*section_height_on_page/3))*cm, -1.5*cm, "SECTION " + str(section_counter +1 + (page-1)*3))
				c.rotate(-90)
				fivecm_notch_interval = int((section_length / 0.05)) + 1
				fivecm_notch_level = start_point
				for i in range(fivecm_notch_interval):
					fivecm_notch_level = start_point+i*section_height_on_page *(0.05 / section_length)
					c.line(2.8*cm,fivecm_notch_level*cm,2.6*cm,fivecm_notch_level*cm)
				twentyfivecm_notch_interval = int((section_length / 0.25)) + 1
				twentyfivecm_notch_level = start_point
				for i in range(twentyfivecm_notch_interval):
					twentyfivecm_notch_level = start_point+i*section_height_on_page *(0.25 / section_length)
					c.line(2.8*cm,twentyfivecm_notch_level*cm,2.4*cm,twentyfivecm_notch_level*cm)
					interval_name = section_length - 0.25*i
					c.setFont("Helvetica", 8)
					c.setFillColor('black')
					c.drawString(1.8*cm, (twentyfivecm_notch_level-0.1)*cm, str(int(100*interval_name)))
		
				for WRC in section:
					request_number = WRC.split(" ")[0]
					if request_number not in label_dict.keys():
						label_dict[request_number] = list()
					upper_limit = start_point + section_height_on_page *(1- section[WRC][0] / section_length)
					lower_limit = start_point + section_height_on_page *(1- section[WRC][1] / section_length)
					c.setFillColor(colour_dict[request_number])
					c.rect(3*cm,lower_limit*cm,3*cm,(upper_limit - lower_limit)*cm, fill=1)
					c.setFillColor('black')
					c.setFont("Helvetica", 8)
					c.drawString(4.1*cm, ((lower_limit+upper_limit)/2-0.1)*cm, request_number)
					descriptor = (WRC.split(" ")[1] + WRC.split(">")[1])
					descriptor_stripped = str()
					for word in descriptor.split(" ")[:len(descriptor.split(" "))-1]:
						descriptor_stripped = descriptor_stripped + " " + word
					c.drawString(6.1*cm, ((lower_limit+upper_limit)/2-0.1)*cm, descriptor_stripped)
#					c.drawString(6.1*cm, ((lower_limit+upper_limit)/2-0.1)*cm, descriptor)
					label_counter = 0
				for request_number in label_dict:
					box_height = 0.5
					start_point = (26 - 0.5*label_counter - box_height)
					c.setFillColor(colour_dict[request_number])
					c.rect(12*cm,(start_point-0.1)*cm,8*cm,(box_height)*cm, fill=1)
					c.setFont("Helvetica", 12)
					c.setFillColor('black')
					c.drawString(12.1*cm, (start_point+box_height-0.5)*cm, request_number + " " + name_dict[request_number])
					label_start_point = start_point+box_height-1
					label_counter = label_counter + 1.5
				section_counter = section_counter + 1
			c.showPage()

	c.save()


if(sections_per_core <= 2):
	draw_short_cores()
else:
	draw_long_cores()
								
