import uuid

import spacy
from psycopg2.extensions import connection as PgConnection
import pytest
from middleware.search_query import SearchQueryEngine
import lorem

class TestSearchQueryEngineInit:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.connection = # Set your PgConnection object here
        self.searchQueryEngine = SearchQueryEngine(self.connection)

    def test_init(self):
        assert isinstance(self.searchQueryEngine.conn, PgConnection), "Connection object not set correctly"
        assert isinstance(self.searchQueryEngine.nlp, spacy.lang.en.English), "NLP object not loaded correctly"

    def test_log_query_results(self):
        """
        Test that logging properly occurs
        depending on course_record_types and location arguments

        :return:
        """
        # Build data sources
        data_sources = {}
        data_sources["data"] = []
        for i in range(10):
            entry = {
                "airtable_uid": uuid.uuid4(),
                "data_source_name": lorem.sentence()
            }
            data_sources["data"].append(entry)

        sample_coarse_record_types = ["crouching", "mice", "better"]
        sample_location = "Lilliput"

        # Test when coarse_record_types and location are both filled
        self.searchQueryEngine.log_query_results(
            coarse_record_types=sample_coarse_record_types,
            location=sample_location,
            data_sources=data_sources
        )
        raise NotImplementedError

        # Test when coarse_record_types and location are both empty
        self.searchQueryEngine.log_query_results(
            coarse_record_types=[],
            location="",
            data_sources=data_sources,
        )
        raise NotImplementedError

        # Test when coarse_record_types is not empty but location is empty
        self.searchQueryEngine.log_query_results(
            coarse_record_types=sample_coarse_record_types,
            location="",
            data_sources=data_sources
        )
        raise NotImplementedError

        # Test when coarse_record_types is empty but location is not empty
        self.searchQueryEngine.log_query_results(
            coarse_record_types=[],
            location=sample_location,
            data_sources=data_sources
        )
        raise NotImplementedError

        pass

    def test_quick_search(self):
        pass

    def test_search_query(self):
        pass

    def test_lemmatize(self):
        """
        Test that nlp component performs as expected, lemmatizing words properly
        :return:
        """
        words = ["running", "better", "mice", "geese", "singing"]
        lemmatized_forms = ["run", "good", "mouse", "goose", "sing"]
        assert self.searchQueryEngine.lemmatize(words) == lemmatized_forms

