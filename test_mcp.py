import asyncio
from app.mcp_client import list_tools, call_tool

async def main():
    print("Tools found:", await list_tools())
    print(await call_tool("lookup_vendor", {"vendor": "Acme Supplies Pvt Ltd"}))
    print(await call_tool("lookup_vendor", {"vendor": "Shady Traders"}))
    print(await call_tool("check_duplicate_invoice",
                          {"invoice_number": "INV-1001", "vendor": "Acme Supplies Pvt Ltd"}))

asyncio.run(main())