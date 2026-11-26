"""The MCP server: the pinned docs index as two tools, over stdio."""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from niu_assistant import index

INSTRUCTIONS = (
    "Public docs from the Neuroinformatics Unit and the projects it "
    "maintains: the NIU how-to guides (the SWC HPC cluster, SSH, SLURM, "
    "SLEAP on the cluster, ceph, cookiecutter, licensing, data sharing, GIN, "
    "electrophysiology), movement, BrainGlobe and photon-mosaic. Use "
    "find_docs to see which pages fit a question, read_doc to read one, and "
    "give the page's link with the answer. If no page covers the question, "
    "say so rather than guessing."
)
FIND_DOCS = (
    "List the pages that match a question, best match first: id, source, "
    "title, a one-line summary and a link. An empty query lists every page."
)
READ_DOC = "Return one page in full, by the id find_docs gave."

server = MCPServer("niu", instructions=INSTRUCTIONS)


@server.tool(description=FIND_DOCS)
def find_docs(query: str = "") -> list[dict[str, str]]:
    return index.find_docs(query)


@server.tool(description=READ_DOC)
def read_doc(id: str) -> str:
    try:
        return index.read_doc(id)
    except (ValueError, OSError) as error:
        raise ToolError(str(error)) from None


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
