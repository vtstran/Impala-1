#!/usr/bin/env python
# Copyright (c) 2012 Cloudera, Inc. All rights reserved.
# General Impala query tests
#
import logging
import pytest
from tests.common.test_vector import *
from tests.common.impala_test_suite import ImpalaTestSuite
from tests.common.test_dimensions import create_uncompressed_text_dimension
from tests.util.test_file_parser import QueryTestSectionReader

class TestQueries(ImpalaTestSuite):
  @classmethod
  def add_test_dimensions(cls):
    super(TestQueries, cls).add_test_dimensions()
    if cls.exploration_strategy() == 'core':
      cls.TestMatrix.add_constraint(lambda v:\
          v.get_value('table_format').file_format == 'parquet')

  @classmethod
  def get_workload(cls):
    return 'functional-query'

  def test_distinct(self, vector):
    if vector.get_value('table_format').file_format == 'hbase':
      pytest.xfail("HBase returns columns in alphabetical order for select distinct *, "
                    "making result verication fail.")
    self.run_test_case('QueryTest/distinct', vector)

  def test_exprs(self, vector):
    # TODO: Enable some of these tests for Avro if possible
    # Don't attempt to evaluate timestamp expressions with Avro tables (which)
    # don't support a timestamp type)"
    table_format = vector.get_value('table_format')
    if table_format.file_format == 'avro':
      pytest.skip()
    if table_format.file_format == 'hbase':
      pytest.xfail("A lot of queries check for NULLs, which hbase does not recognize")
    self.run_test_case('QueryTest/exprs', vector)

    # This will change the current database to matching table format and then execute
    # select current_database(). An error will be thrown if multiple values are returned.
    current_db = self.execute_scalar('select current_database()', vector=vector)
    assert current_db == QueryTestSectionReader.get_db_name(table_format)

  def test_hdfs_scan_node(self, vector):
    self.run_test_case('QueryTest/hdfs-scan-node', vector)

  def test_file_partitions(self, vector):
    self.run_test_case('QueryTest/hdfs-partitions', vector)

  def test_limit(self, vector):
    if vector.get_value('table_format').file_format == 'hbase':
      pytest.xfail("IMPALA-283 - select count(*) produces inconsistent results")
    self.run_test_case('QueryTest/limit', vector)

  def test_top_n(self, vector):
    if vector.get_value('table_format').file_format == 'hbase':
      pytest.xfail(reason="IMPALA-283 - select count(*) produces inconsistent results")
    # QueryTest/top-n is also run in test_sort with disable_outermost_topn = 1
    self.run_test_case('QueryTest/top-n', vector)

  def test_union(self, vector):
    self.run_test_case('QueryTest/union', vector)

  def test_sort(self, vector):
    if vector.get_value('table_format').file_format == 'hbase':
      pytest.xfail(reason="IMPALA-283 - select count(*) produces inconsistent results")
    vector.get_value('exec_option')['disable_outermost_topn'] = 1
    self.run_test_case('QueryTest/sort', vector)
    # We can get the sort tests for free from the top-n file
    self.run_test_case('QueryTest/top-n', vector)

  def test_subquery(self, vector):
    self.run_test_case('QueryTest/subquery', vector)

  def test_subquery_limit(self, vector):
    self.run_test_case('QueryTest/subquery-limit', vector)

  def test_empty(self, vector):
    self.run_test_case('QueryTest/empty', vector)

  def test_views(self, vector):
    if vector.get_value('table_format').file_format == "hbase":
      pytest.xfail("TODO: Enable views tests for hbase")
    self.run_test_case('QueryTest/views', vector)

  def test_with_clause(self, vector):
    if vector.get_value('table_format').file_format == "hbase":
      pytest.xfail("TODO: Enable with clause tests for hbase")
    self.run_test_case('QueryTest/with-clause', vector)

  def test_misc(self, vector):
    table_format = vector.get_value('table_format')
    if table_format.file_format in ['hbase', 'rc', 'parquet']:
      msg = ("Failing on rc/snap/block despite resolution of IMP-624,IMP-503. "
             "Failing on parquet because tables do not exist")
      pytest.xfail(msg)
    self.run_test_case('QueryTest/misc', vector)

  def test_null_data(self, vector):
    if vector.get_value('table_format').file_format == 'hbase':
      pytest.xfail("null data does not appear to work in hbase")
    self.run_test_case('QueryTest/null_data', vector)

# Tests in this class are only run against text/none either because that's the only
# format that is supported, or the tests don't exercise the file format.
class TestQueriesTextTables(ImpalaTestSuite):
  @classmethod
  def add_test_dimensions(cls):
    super(TestQueriesTextTables, cls).add_test_dimensions()
    cls.TestMatrix.add_dimension(create_uncompressed_text_dimension(cls.get_workload()))

  @classmethod
  def get_workload(cls):
    return 'functional-query'

  def test_overflow(self, vector):
    self.run_test_case('QueryTest/overflow', vector)

  def test_data_source_tables(self, vector):
    self.run_test_case('QueryTest/data-source-tables', vector)

  def test_distinct_estimate(self, vector):
    # These results will vary slightly depending on how the values get split up
    # so only run with 1 node and on text.
    vector.get_value('exec_option')['num_nodes'] = 1
    self.run_test_case('QueryTest/distinct-estimate', vector)

  def test_mixed_format(self, vector):
    self.run_test_case('QueryTest/mixed-format', vector)

  def test_values(self, vector):
    self.run_test_case('QueryTest/values', vector)


