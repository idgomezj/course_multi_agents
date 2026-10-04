# Demand spike and promotion management

Use for promotions, commercial events, unexpected spikes, promotion cancellation,
or a sharp disagreement between recent demand and confirmed orders.

1. Retrieve promotion and forecast-override policy evidence.
2. Run the Team 1 PyTorch forecast and uncertainty model for the affected product.
3. Compare at least one classical forecast when the PyTorch result is materially
   different from confirmed orders or the visible event.
4. Distinguish:
   - **real upside**: promotion/event plus orders support the increase;
   - **uncertain upside**: weak orders or high model uncertainty;
   - **cancelled/failed promotion**: remove the promotion uplift immediately.
5. For real/uncertain upside, protect service with a targeted early-week safety
   buffer. Do not permanently lift every week.
6. For cancellation/drop, consume existing finished goods first and reduce later
   production to avoid residual inventory.
7. Check capacity before moving production forward. Then explode BOM, net existing
   inventory/open POs, and buy only the shortage.
8. Compare total candidate-plan cost and validate the complete plan before finalizing.
