# Energy Data Insights

Weekly analysis of UK energy market data — live datasets, Power BI dashboards, and insights, built as an ongoing public series.

## About
This project tracks real UK energy market data over time, turning it into 
clear visuals and analysis. I am Ahsan Bin Ahmed, an Energy Markets Specialist in the UK. Aiming to build these as a 
public portfolio of applied data work.

## Week 1: Carbon Intensity (National Grid ESO)

**Source:** [Carbon Intensity API](https://carbonintensity.org.uk/) — live, 
public, no authentication required.

**What's in this analysis:**
- Actual vs Forecast carbon intensity (gCO2/kWh) over 7 days
- Generation mix by fuel type (gas, wind, solar, nuclear, etc.) over the 
  same period

**Files:**
- `ABA_CarbonIntensity.pbix` — Power BI file
- `screenshots/` — chart images (for quick viewing without opening Power BI)

**Key observation:**
Over the week analysed, National Grid ESO's forecast 
carried a systematic time-of-day bias rather than random error: it 
consistently overestimated carbon intensity overnight (11pm–7am, by 
8-16 gCO2/kWh) and underestimated it during the afternoon peak 
(3pm-5pm, by 11-19 gCO2/kWh). Mean absolute error across the week was 
10.3 gCO2/kWh. Correlation with generation mix was modest, with imports 
and nuclear share showing the strongest (though still weak) 
relationship — worth tracking over further weeks before drawing a firm 
conclusion.

## Roadmap
Future weeks will cover: NESO forecast accuracy, Elexon settlement data, 
DESNZ energy trends, and Ofgem data portal — each
