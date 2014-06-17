# -*- coding: utf-8 -*-
import xlrd
from difflib import SequenceMatcher

def string_cleaning(text):
	text = text.replace(' ', '')
	text = text.replace(u'á', 'a')
	text = text.replace(u'é', 'e')
	text = text.replace(u'í', 'i')
	text = text.replace(u'ó', 'o')
	text = text.replace(u'ú', 'u')
	text = text.replace(u'ñ', 'n')
	return text.lower()
	
def find_closers(seq_list, seq_target, threshold=1.0):
	
	min_ratio = 0
	closer = ''
	
	seq_target = string_cleaning(seq_target)
	
	for seq in seq_list:
		ratio = SequenceMatcher(None, seq_target, string_cleaning(seq)).ratio()
		if ratio > min_ratio:
			min_ratio = ratio
			closer = seq
	
	if min_ratio >= threshold:
		return closer, min_ratio
	else:
		return None, None
