"""Menu."""


class Menu:
    """HTML Menu."""

    def __init__(self, items):
        self.items = items

    def html(self):
        """Return HTML Code."""
        html = """
<div id="bottom_menu" class="fixed-action-btn horizontal" style="bottom: 20px; right: 25px;">
    <a id="menu" class="btn-floating btn-large red" >
        <i class="large material-icons">menu</i>
    </a>
    <ul>"""
        for idx, items in self.items.items():
            html += f"""
        <li>
            <a id="{idx}" class="btn-floating" title="{items["title"]}">
                <i class="material-icons">{items["icon"]}</i>
            </a>
        </li>
"""
        html += "</ul></div>"
        return html

    def javascript(self):
        """Return Javascript Code."""
        javascript = ""
        for idx, items in self.items.items():
            if "ajax" in items:
                javascript += f"""
$("#{idx}").click(function () {{
    $("#bottom_menu").removeClass("active")
"""
                if "loading_page" in items:
                    javascript += f"""
    $.LoadingOverlay("show", {items['loading_page']});
"""

                javascript += f"""
    $.ajax({{
        type: '{items["ajax"]["method"]}',
        url: '{items["ajax"]["url"]}'
    }})
        .done(function (data) {{
            $.LoadingOverlay("hide");
            data = JSON.parse(JSON.stringify(data))
            let status = data["result"]["status"];
            if (status == false) {{

            }}else{{
                location.reload();
            }}
        }})
}});
"""
        return javascript

    def css(self):
        """Return CSS Code."""
        css = ""
        for idx, items in self.items.items():
            if "css" in items:
                css += f"""
#{idx} {{
  {items["css"]}
}}
"""
        return css
