import os
import time
import click
import random
import requests
from contextlib import closing


'''检查是否有存在该文件夹，若不存在，则新建一个'''
def checkDir(dirpath):
	if not os.path.exists(dirpath):
		os.mkdir(dirpath)
		return False
	return True


'''获取B站前top_n个小视频的链接'''
def getVideoTopNLinks(top_n):
	assert top_n > 0, '<top_n> in function getVideoTopNLinks must be larger than zero.'
	print('[INFO]: Start to get video topn links...')
	info_url = 'http://api.vc.bilibili.com/board/v1/ranking/top?'
	headers = {
				'Referer': 'http://vc.bilibili.com/p/eden/rank',
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
			}
	params_base = {
					'page_size': 10,
					'next_offset': -10,
					'tag': '今日热门',
					'platform': 'pc'
					}
	video_infos = []
	while True:
		params_base['next_offset'] += params_base['page_size']
		if top_n <= 10:
			params_base['page_size'] = top_n
			top_n = 0
		else:
			top_n = top_n - 10
		try:
			res = requests.get(info_url, params=params_base, headers=headers)
			items = res.json()['data']['items']
			for item in items:
				title = item['item']['description']
				for char in '/:：*?？"<>|':
					title = title.replace(char, '')
				link = item['item']['video_playurl']
				video_infos.append([title, link])
				print('[INFO]: Got %s...' % title)
		except:
			print('[Warnning]: Something error when getting video links...')
		if top_n <= 0:
			break
		time.sleep(random.random() * 2)
	print('[INFO]: Finish, get %d links in total...' % (len(video_infos)))
	return video_infos


'''下载单个视频'''
def downloadVideo(video_info, savepath):
	checkDir(savepath)
	savename, video_link = '%s.mp4' % video_info[0], video_info[1]
	headers = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
			}
	with closing(requests.get(video_link, headers=headers, stream=True, verify=False)) as res:
		total_size = int(res.headers['content-length'])
		if res.status_code == 200:
			label = '[%s, FileSize]:%0.2f MB' % (savename, total_size/(1024*1024))
			with click.progressbar(length=total_size, label=label) as progressbar:
				with open(os.path.join(savepath, savename), "wb") as f:
					for chunk in res.iter_content(chunk_size=1024):
						if chunk:
							f.write(chunk)
							progressbar.update(1024)


'''主函数'''
if __name__ == '__main__':
	top_n = 100
	savepath = 'bilibilivideos'
	video_infos = getVideoTopNLinks(top_n)
	for video_info in video_infos:
		try:
			downloadVideo(video_info, savepath)
		except:
			print('[Warnning]: Fail to download %s...' % video_info[1])
		time.sleep(random.random() * 2)