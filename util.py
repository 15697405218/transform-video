import json
import logging

import av
import wx

logger = logging.getLogger('MyLogger')


# 可能每一个kv转换对都需要单独做对应的方法，因为各个参数处理不容易一致，要么就做面板手动选择这些需要的参数
def convert_video(input_path, output_path, input_format, output_format, codec_name_video, codec_name_audio,
                  out_file_name, dialog):
    if output_format == "mkv":
        output_format = 'matroska'
    try:
        # 打开输入容器
        input_container = av.open(input_path, format=input_format)

        # 打开输出容器并设置格式
        output_container = av.open(output_path + "\\" + out_file_name + '.' + output_format, 'w',
                                   format=output_format)

        # 添加视频流到输出容器
        logger.info(f"开始转换：目标视频容器：{output_format}，视频编码：{codec_name_video}，音频编码：{codec_name_audio}")
        video_stream = output_container.add_stream(codec_name_video)
        codec_out_video = video_stream.codec_context
        # total_duration = input_container.duration  # 视频总时长，单位通常是时间基准（如秒）
        # logger.info(total_duration)
        # frame_rate = input_container.streams.video[0].average_rate  # 帧率
        # logger.info(frame_rate)

        # # 估算总帧数
        # estimated_total_frames = int(total_duration * frame_rate)
        #
        # dialog.m_gauge1.SetRange(1000)

        # 复制视频编解码器上下文参数
        codec_out_video.width = input_container.streams.video[0].codec_context.width
        codec_out_video.height = input_container.streams.video[0].codec_context.height
        # codec_out_video.pix_fmt = "yuv420p"
        # codec_out_video.bit_rate = input_container.streams.video[0].codec_context.bit_rate

        # 添加音频流到输出容器 (如果存在)
        if input_container.streams.audio:
            audio_stream = output_container.add_stream(codec_name_audio)

        # 添加字幕流到输出容器 (如果存在)
        if input_container.streams.subtitles:
            subtitle_stream = output_container.add_stream('srt')

        # 解码和编码视频
        for packet in input_container.demux():
            if packet.stream.type == 'video':
                for frame in packet.decode():
                    frame.pts = None  # 清除时间戳，强制重新计算
                    for encoded_packet in video_stream.encode(frame):
                        output_container.mux(encoded_packet)
                        logger.info(frame.index)
                        # if frame.index % (estimated_total_frames // 100) == 0:
                        #     wx.CallAfter(dialog.UpdateProgress, frame.index)
            elif packet.stream.type == 'audio' and 'audio_stream' in locals():
                for frame in packet.decode():
                    frame.pts = None
                    for encoded_packet in audio_stream.encode(frame):
                        output_container.mux(encoded_packet)
                        # wx.CallAfter(dialog.m_gauge1.UpdateProgress, i)
            elif packet.stream.type == 'subtitles' and 'subtitle_stream' in locals():
                for frame in packet.decode():
                    frame.pts = None
                    encoded_packet = subtitle_stream.encode(frame)
                    output_container.mux(encoded_packet)
                    # wx.CallAfter(dialog.m_gauge1.UpdateProgress, i)

        # 关闭输入和输出容器
        input_container.close()
        output_container.close()
        dialog.Close()
        logger.info("转换完成")
        return True
    except Exception as e:
        logger.error(f"转换失败: {e}")
        return False


def query_supported_codecs_from_json(format_name):
    # 从JSON文件中读取数据
    try:
        with open('format_codec_map.json', 'r') as json_file:
            common_format_codec_map = json.load(json_file)
    except FileNotFoundError:
        return "JSON file not found. Please ensure 'format_codec_map.json' exists."

    # 查询给定格式
    if format_name in common_format_codec_map:
        codecs = common_format_codec_map[format_name]
        video_codecs = ', '.join(codecs['video'])
        audio_codecs = ', '.join(codecs['audio'])
        return f"Supported video codecs for {format_name}: {video_codecs}\nSupported audio codecs for {format_name}: {audio_codecs}"
    else:
        return f"Format '{format_name}' is not included in the simplified mapping."

# # 示例调用
# input_path = "a.mp4"
# output_path = "output.flv"
# input_format = None  # 如果你不确定输入格式，可以让PyAV自动检测
# output_format = "flv"
#
# result = convert_video(input_path, output_path, input_format, output_format)
# if result:
#     print("视频和音频转换成功！")
# else:
#     print("视频和音频转换失败。")
