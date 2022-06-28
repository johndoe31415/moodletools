#!/usr/bin/python3
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

import sys
import json
import csv
import os
import collections
import math
from FriendlyArgumentParser import FriendlyArgumentParser
from GradeComputation import GradeComputation

parser = FriendlyArgumentParser(description = "Grade computation of coursework.")
parser.add_argument("-f", "--force", action = "store_true", help = "Overwrite output files if they already exist.")
parser.add_argument("-c", "--cluster-column-number", metavar = "column_number", type = int, help = "Cluster results by this column number.")
parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increases verbosity. Can be specified multiple times to increase.")
parser.add_argument("-p", "--total-points", metavar = "points", type = float, default = 100, help = "Total number of points achievable. Defaults to %(default).0f.")
parser.add_argument("-m", "--min-threshold-percent", metavar = "percent", type = float, default = 50, help = "Minimum threshold in percent. Defaults to %(default).0f.")
parser.add_argument("-M", "--max-threshold-percent", metavar = "percent", type = float, default = 90, help = "Maximum threshold in percent. Defaults to %(default).0f.")
parser.add_argument("csv_input", help = "CSV file which stores the grades, one per row.")
parser.add_argument("col_number", metavar = "column_number", type = int, help = "Column number to take as input points of.")
parser.add_argument("csv_output", help = "CSV file which is augmented by the grades and written.")

args = parser.parse_args(sys.argv[1:])

class Grader():
	def __init__(self, args):
		self._args = args
		self._grader = GradeComputation(min_threshold_percent = self._args.min_threshold_percent, max_threshold_percent = self._args.max_threshold_percent)
		self._given_grades = collections.defaultdict(list)

	def _run_line(self, line):
		if len(line) < self._args.col_number:
			# Too few rows
			self._writer.writerow(line)
			return


		invalue = line[self._args.col_number - 1]
		invalue = invalue.replace(",", ".")
		try:
			invalue = float(invalue)
		except ValueError:
			# Not a value value
			self._writer.writerow(line)
			return

		# Fill colums up
		if len(line) < self._col_count:
			line += [ "" ] * (self._col_count - len(line))

		percent_value = (invalue / self._args.total_points) * 100
		grade = self._grader.grade(percent_value)

		line.append(grade.grade)
		line.append(grade.gradestr)
		if grade.failed:
			missing_points = (self._args.min_threshold_percent - percent_value) / 100 * self._args.total_points
			line.append(f"{missing_points:.1f} points missing")

		if self._args.cluster_column_number is None:
			cluster = "default"
		else:
			cluster = line[self._args.cluster_column_number - 1]
		self._given_grades[cluster].append(grade)
		self._writer.writerow(line)

	def run(self):
		if self._args.verbose >= 2:
			for percent in range(math.floor(self._args.min_threshold_percent), math.ceil(self._args.max_threshold_percent) + 1):
				points = percent / 100 * self._args.total_points
				grade = self._grader.grade(percent)
				print(f"{percent:3d}%  {points:5.1f}  {grade.grade:.1f} {grade.gradestr}")
			print()

		if (not self._args.force) and os.path.exists(self._args.csv_output):
			raise Exception(f"Refusing to overwrite: {self._args.csv_output}")

		with open(self._args.csv_input) as in_f:
			self._in_data = [ line for line in csv.reader(in_f) ]

		self._col_count = max(len(line) for line in self._in_data)

		with open(self._args.csv_output, "w") as out_f:
			self._writer = csv.writer(out_f)
			for line in self._in_data:
				self._run_line(line)

		for (cluster_name, cluster_results) in sorted(self._given_grades.items()):
			print("Cluster     : %s" % (cluster_name))
			print("Graded exams: %d" % (len(cluster_results)))
			print("Breakdown:")

			for (grade, count) in sorted(collections.Counter((grade.grade for grade in cluster_results)).most_common()):
				print("   %.1f    %d" % (grade, count))
			print()

			for ((gradestr_group, gradestr), count) in sorted(collections.Counter(((grade.gradestr_group, grade.gradestr) for grade in cluster_results)).most_common()):
				print("   %-20s    %d" % (gradestr, count))

			print()
			avg = sum(grade.grade for grade in cluster_results) / len(cluster_results)
			print("Average: %.1f" % (avg))
			print()
			print()


grader = Grader(args)
grader.run()
