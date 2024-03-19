import asyncio
import json
import logging
import sys
import threading

import av


import wx

from logger import TextCtrlHandler
from util import convert_video
import wx.xrc

###########################################################################
## Class MyDialog1
###########################################################################

class MyDialog1 ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 600,60), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_gauge1 = wx.Gauge( self, wx.ID_ANY, 100, wx.Point( -1,-1 ), wx.Size( 600,20 ), wx.GA_HORIZONTAL )
		self.m_gauge1.SetValue( 0 )
		bSizer1.Add( self.m_gauge1, 0, wx.ALL, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass

	def UpdateProgress(self, value):
		self.m_gauge1.SetValue(value)


class MyFrame(wx.Frame):
	def on_combo_select(self,event):
		print(self.common_format_codec_map[self.FindWindowByName("output_format").Value]['video'])
		combo_codec_video = (self.FindWindowByName("combo_codec_video"))
		combo_codec_video.SetItems(self.common_format_codec_map[self.FindWindowByName("output_format").Value]['video'])
		combo_codec_video.SetValue(self.common_format_codec_map[self.FindWindowByName("output_format").Value]['video'][0])

		combo_codec_audio = (self.FindWindowByName("combo_codec_audio"))
		combo_codec_audio.SetItems(self.common_format_codec_map[self.FindWindowByName("output_format").Value]['audio'])
		combo_codec_audio.SetValue(
			self.common_format_codec_map[self.FindWindowByName("output_format").Value]['audio'][0])



	def transform_onclick(self,event):
		# 打开输入视频文件
		self.FindWindowByName("transform").Disable()
		input_file_path= self.FindWindowByName("text_file").Value
		output_file_path = self.FindWindowByName("text_out_file_path").Value
		output_file_format = self.FindWindowByName("output_format").Value
		combo_codec_video = self.FindWindowByName("combo_codec_video").Value
		combo_codec_audio = self.FindWindowByName("combo_codec_audio").Value
		out_file_name = self.FindWindowByName("out_file_name").Value

		dialog = MyDialog1(self)
		# dialog.Show()# 先注释，不太好推断进度


		if combo_codec_video and out_file_name is not None:
			# convert_video(input_file_path,output_file_path,None,output_file_format,codec_name)
			conversion_thread = threading.Thread(target=convert_video, args=(input_file_path, output_file_path, None, output_file_format, combo_codec_video,combo_codec_audio,out_file_name,dialog))
			conversion_thread.daemon = True
			conversion_thread.start()

		else:
			print("请选择编解码器,填写文件名")
		self.FindWindowByName("transform").Enable()


	def select_onclick(self, event):

		# 创建一个文件选择框
		filedialog = wx.FileDialog(self, "选择文件", "", "", "", wx.FD_OPEN)
		wildcard = "video files (*.3GP;*.3GPP;*.AAC;*.AIFF;*.AIF;*.AMR;*.APE;*.ASF;*.ASS;*.AVI;*.CAF;*.DTS;*.DV;*.EAC3;*.FLAC;*.FLV;*.GIF;*.H261;*.H263;*.H264;*.H265;*.HEVC;*.M4A;*.M4B;*.M4V;*.MKV;*.MOV;*.MP2;*.MP3;*.MP4;*.MPEG;*.MPG;*.MTS;*.MXF;*.OGG;*.OGA;*.OGV;*.OPUS;*.PCM;*.RA;*.RAM;*.RAWVIDEO;*.ROQ;*.S16LE;*.S24LE;*.S32LE;*.SB24LE;*.SB32LE;*.SIPR;*.SMI;*.SRT;*.SSA;*.SSV;*.SUB;*.SWF;*.TAK;*.THEORA;*.TS;*.TTA;*.VOB;*.VORBIS;*.WAV;*.WEBM;*.WMA;*.WMV;*.WV;*.Y4M;*.YUV4MPEGPIPE;*.YUV4MPEGPSIZE;*.YUV4MPEGVIDEO)"
		filedialog.SetWildcard(wildcard)

		# 显示文件选择框
		if filedialog.ShowModal() == wx.ID_OK:
			# 获取用户选择的文件路径
			filename = filedialog.GetPath()
			text = self.FindWindowByName("text_file")
			text.SetValue(filename)

			print(text)
			# 处理文件
			print(f"选择了文件：{filename}")
		filedialog.Destroy()


	def out_file_path_onclick(self,event):
		dir_dialog = wx.DirDialog(None, "选择文件夹", style=wx.DD_DEFAULT_STYLE)

		if dir_dialog.ShowModal() == wx.ID_OK:
			path = dir_dialog.GetPath()
			print(f"您选择了文件夹：{path}")
			self.FindWindowByName("text_out_file_path").SetValue(path)
		else:
			print("您取消了选择文件夹")
		dir_dialog.Destroy()


	def __init__(self):
		super().__init__(None, title="GridBagSizer Example",size=(800, 600))
		self.SetSizeHints(minW=800, minH=600,maxW=800,maxH=600)
		self.common_format_codec_map = {}
		# 创建一个GridBagSizer对象
		sizer = wx.GridBagSizer(hgap=10, vgap=10)

		# 创建一个下拉框
		# 从JSON文件中读取数据
		try:
			with open('format_codec_map.json', 'r') as json_file:
				self.common_format_codec_map = json.load(json_file)
				output_formats = []
				for key in self.common_format_codec_map.keys():
					output_formats.append(key)
				combo = wx.ComboBox(self)
				combo.SetItems(output_formats)
				# 设置下拉框的初始值
				combo.SetValue(output_formats[0])
				combo.SetName("output_format")
				combo.Bind(wx.EVT_COMBOBOX, self.on_combo_select)

		except FileNotFoundError:
			print(FileNotFoundError)


		# 将下拉框添加到窗口中
		sizer.Add(combo, pos=(0, 1), span=(1, 1), flag=wx.EXPAND)
		combo_codec_video = wx.ComboBox(self)
		combo_codec_video.SetName("combo_codec_video")
		sizer.Add(combo_codec_video,pos=(0,2),span=(1, 1), flag=wx.EXPAND)
		# 添加一个按钮转换
		button_transform = wx.Button(self, label="转换")
		button_transform.Bind(wx.EVT_BUTTON,self.transform_onclick)
		button_transform.SetName("transform")
		sizer.Add(button_transform, pos=(0, 0))

		# 添加一个按钮
		button_select = wx.Button(self, label="选择文件")
		button_select.Bind(wx.EVT_BUTTON,self.select_onclick)
		sizer.Add(button_select, pos=(0, 4))
		#添加输出目录选择按钮
		button_out_file_path = wx.Button(self,label="选择输出目录")
		button_out_file_path.Bind(wx.EVT_BUTTON,self.out_file_path_onclick)
		sizer.Add(button_out_file_path,pos= (0,6))

		#添加文本框，显示选择文件信息
		text_file = wx.TextCtrl(self)
		text_file.SetName("text_file")
		text_file.SetValue("")
		sizer.Add(text_file,pos = (0,3))

		#添加文本框，显示输出目录
		text_out_file_path = wx.TextCtrl(self)
		text_out_file_path.SetName("text_out_file_path")
		text_out_file_path.SetValue("")
		sizer.Add(text_out_file_path,pos=(0,5))

		# 将选择音频编码下拉框添加到窗口中
		combo_codec_audio = wx.ComboBox(self)
		combo_codec_audio.SetName("combo_codec_audio")
		sizer.Add(combo_codec_audio,pos=(1,2),span=(1, 1), flag=wx.EXPAND)

		# 创建文本标签
		file_label = wx.StaticText(self, label="输出文件名:", pos=(10, 10),style=wx.ALIGN_CENTER)
		sizer.Add(file_label,pos=(2,0))
		# 创建文本框
		out_file_name = wx.TextCtrl(self, pos=(80, 10))
		out_file_name.SetName("out_file_name")
		sizer.Add(out_file_name,pos=(2,1))

		# 创建一个只读的多行文本框用于显示日志
		log_text_ctrl = wx.TextCtrl(self, style=wx.TE_READONLY | wx.TE_MULTILINE)
		# 创建日志记录器
		logger = logging.getLogger('MyLogger')
		logger.setLevel(logging.DEBUG)

		# 创建自定义处理器，并添加到日志记录器
		handler = TextCtrlHandler(log_text_ctrl)
		formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		# 将文本框添加到布局管理器，并让它跨5列
		sizer.Add(log_text_ctrl, pos=(9, 0), span=(10, 9), flag=wx.EXPAND)

		# 设置窗口的布局器
		self.SetSizer(sizer)


if __name__ == "__main__":
	app = wx.App()
	frame = MyFrame()
	frame.Show()
	app.MainLoop()


