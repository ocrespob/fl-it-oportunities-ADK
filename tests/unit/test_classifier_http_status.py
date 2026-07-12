# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from app.classifier import classify_with_mock, WebsiteStatus


def test_classify_with_mock_http_403() -> None:
    """Verify that HTTP 403 status is classified as Modern rather than Broken/Missing, and pitches security."""
    res = classify_with_mock(
        business_name="The Black Law Company",
        website_url="http://theblacklawcompany.com/",
        review_count=125,
        scraped_text="Failed to load website. HTTP Status: 403",
        http_status=403,
    )
    assert res["website_status"] != WebsiteStatus.BROKEN_OR_MISSING
    assert res["website_status"] == WebsiteStatus.MODERN
    assert (
        "firewall" in res["sales_reasoning"].lower()
        or "waf" in res["sales_reasoning"].lower()
        or "forbidden" in res["sales_reasoning"].lower()
    )
    assert (
        "security" in res["online_presence"].lower()
        or "protected" in res["online_presence"].lower()
        or "firewall" in res["online_presence"].lower()
    )


def test_classify_with_mock_http_404() -> None:
    """Verify that HTTP 404 status is classified as Broken/Missing."""
    res = classify_with_mock(
        business_name="Nonexistent Biz",
        website_url="http://nonexistent.com/",
        review_count=10,
        scraped_text="Failed to load website. HTTP Status: 404",
        http_status=404,
    )
    assert res["website_status"] == WebsiteStatus.BROKEN_OR_MISSING
