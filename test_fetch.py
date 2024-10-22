import asyncio

from app.utils.amazon import fetch_desc


# Constants
URL: str = (
  "https://www.amazon.com/SHAPERX-Bodysuit-Shapewear-Sculpting-SZ5215-Black-S/dp/B0B1HR89H4?ref=dlx_deals_dg_dcl_B0B1HR89H4_dt_sl14_3f"
)

# Async entry
async def main():
  print(await fetch_desc(URL))

# Main entry
if __name__ == '__main__':
  asyncio.run(main())
