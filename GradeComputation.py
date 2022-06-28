#	moodletools - Collection of scripts that are boilerplate between backend and MOODLE
#	Copyright (C) 2022-2022 Johannes Bauer
#
#	This file is part of moodletools.
#
#	moodletools is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	moodletools is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with moodletools; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import collections

class GradeComputation():
	_ComputedGrade = collections.namedtuple("ComputedGrade", [ "percent", "grade", "gradestr", "gradestr_group", "failed" ])

	def __init__(self, min_threshold_percent = 50, max_threshold_percent = 90):
		self._min_threshold_percent = min_threshold_percent
		self._max_threshold_percent = max_threshold_percent

	@staticmethod
	def _truncate(value):
		return int(value * 10) / 10

	@staticmethod
	def _gradestr(grade):
		if grade <= 1.5:
			return (0, "sehr gut", False)
		elif grade <= 2.5:
			return (1, "gut", False)
		elif grade <= 3.5:
			return (2, "befriedigend", False)
		elif grade <= 4.0:
			return (3, "ausreichend", False)
		else:
			return (4, "nicht ausreichend", True)

	def _compute_grade(self, percent):
		if percent < self._min_threshold_percent:
			return 5.0
		elif percent >= self._max_threshold_percent:
			return 1.0
		else:
			ratio = (percent - self._min_threshold_percent) / (self._max_threshold_percent - self._min_threshold_percent)
			return self._truncate(4.0 - (ratio * 3.0))

	def grade(self, percent):
		grade = self._compute_grade(percent)
		(gradestr_group, gradestr, failed) = self._gradestr(grade)
		return self._ComputedGrade(percent = percent, grade = grade, gradestr = gradestr, gradestr_group = gradestr_group, failed = failed)
