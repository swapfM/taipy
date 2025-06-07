# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import inspect
import os
import warnings

from taipy.gui import Gui, Markdown


def test_favicon(gui: Gui, helpers):
    with warnings.catch_warnings(record=True):
        gui._set_frame(inspect.currentframe())
        gui.add_page("test", Markdown("#This is a page"))
        gui.run(run_server=False)
        client = gui._server.test_client()
        # WS client and emit
        ws_client = gui._server._ws.test_client(gui._server.get_flask())
        # Get the jsx once so that the page will be evaluated -> variable will be registered
        sid = helpers.create_scope_and_get_sid(gui)
        client.get(f"/taipy-jsx/test/?client_id={sid}")
        gui.set_favicon("https://newfavicon.com/favicon.png")
        # assert for received message (message that would be sent to the front-end client)
        msgs = ws_client.get_received()
        assert msgs
        assert msgs[0].get("args", {}).get("type", None) == "FV"
        assert msgs[0].get("args", {}).get("payload", {}).get("value", None) == "https://newfavicon.com/favicon.png"


def test_root_favicon_is_served(tmp_path, gui: Gui):
    # Create a dummy favicon.png in the root (simulated by tmp_path)
    favicon_path = tmp_path / "favicon.png"
    dummy_favicon_content = b"\x89PNG\r\n\x1a\nDummyIcon"
    with open(favicon_path, "wb") as f:
        f.write(dummy_favicon_content)

    # Change working dir temporarily to simulate root directory containing favicon
    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        with warnings.catch_warnings(record=True):
            gui._set_frame(inspect.currentframe())
            gui.add_page("test", Markdown("# Page"))
            gui.run(favicon="favicon.png", run_server=False)
            client = gui._server.test_client()

            # Request the favicon
            response = client.get("/favicon.png")
            assert response.status_code == 200
            assert response.data == dummy_favicon_content
            assert response.mimetype == "image/png"
    finally:
        os.chdir(old_cwd)  # Restore original working dir
