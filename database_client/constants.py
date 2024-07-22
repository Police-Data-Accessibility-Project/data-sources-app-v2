# These columns are used when pulling from the data sources table
DATA_SOURCES_ORIGINAL_COLUMNS = [
    "name",
    "submitted_name",
    "last_approval_editor"]
# These columns are used when pulling from the Agency_Data_Sources_View table
DATA_SOURCES_VIEW_COLUMNS = [
    "data_source_name",
    "data_source_submitted_name",
    "data_source_last_approval_editor",
]

# These columns are the same whether in the Agency_Data_Sources_View table or the data_sources table
DATA_SOURCES_AGNOSTIC_COLUMNS = [
    "description",
    "record_type",
    "source_url",
    "agency_supplied",
    "supplying_entity",
    "agency_originated",
    "originating_entity",
    "agency_aggregation",
    "coverage_start",
    "coverage_end",
    "source_last_updated",
    "retention_schedule",
    "detail_level",
    "number_of_records_available",
    "size",
    "access_type",
    "data_portal_type",
    "record_format",
    "update_frequency",
    "update_method",
    "tags",
    "readme_url",
    "scraper_url",
    "data_source_created",
    "airtable_source_last_modified",
    "url_status",
    "rejection_note",
    "agency_described_submitted",
    "agency_described_not_in_database",
    "approval_status",
    "record_type_other",
    "data_portal_type_other",
    "records_not_online",
    "data_source_request",
    "url_button",
    "tags_other",
    "access_notes",
    "last_cached",
]
DATA_SOURCES_NEEDS_IDENTIFICATION_COLUMNS = DATA_SOURCES_AGNOSTIC_COLUMNS + DATA_SOURCES_ORIGINAL_COLUMNS
DATA_SOURCES_APPROVED_COLUMNS = DATA_SOURCES_AGNOSTIC_COLUMNS + DATA_SOURCES_VIEW_COLUMNS
RESTRICTED_DATA_SOURCE_COLUMNS = [
    "rejection_note",
    "data_source_request",
    "approval_status",
    "airtable_uid",
    "airtable_source_last_modified",
]

AGENCY_DATA_SOURCE_VIEW_COLUMNS = [
    "data_source_id",
    "agency_id",
    "agency_name",
    "homepage_url",
    "count_data_sources",
    "agency_type",
    "agency_submitted_name",
    "jurisdiction_type",
    "state_iso",
    "municipality",
    "county_fips",
    "county_name",
    "lat",
    "lng",
    "data_sources",
    "no_web_presence",
    "airtable_agency_last_modified",
    "data_sources_last_updated",
    "approved",
    "rejection_reason",
    "agency_last_approval_editor",
    "agency_created",
    "county_airtable_uid",
    "defunct_year",
] + DATA_SOURCES_AGNOSTIC_COLUMNS + DATA_SOURCES_VIEW_COLUMNS
