import pandas as pd
import math

def generate_mrp_final_full():
    # --- 1. DATA INPUT ---
    gross_requirements_p1_p6 = [100, 50, 150, 80, 120, 60]
    cost_per_order = 500      
    holding_cost_per_unit = 5 
    initial_inventory = 50    
    lead_time = 1             
    safety_stock = 30         

    # --- 2. HITUNG EOQ (Q*) ---
    avg_demand = sum(gross_requirements_p1_p6) / len(gross_requirements_p1_p6)
    eoq_q = round(math.sqrt((2 * avg_demand * cost_per_order) / holding_cost_per_unit))
    
    # --- 3. PREPARASI DATA ---
    periods = [("P" + str(i)) for i in range(0, 7)]
    gross_req = [0] + gross_requirements_p1_p6
    beg_inv = [0] * 7
    end_inv = [0] * 7
    planned_rec = [0] * 7
    planned_rel = [0] * 7

    # --- 4. LOGIKA MRP (KELIPATAN EOQ + SAFETY STOCK) ---
    current_inv = initial_inventory
    for i in range(1, 7):
        beg_inv[i] = current_inv
        
        # Kebutuhan Bersih untuk menjaga Safety Stock
        net_req = gross_req[i] + safety_stock - beg_inv[i]
        
        if net_req > 0:
            # Jika butuh, pesan dalam kelipatan EOQ (1x, 2x, 3x...)
            multiplier = math.ceil(net_req / eoq_q)
            planned_rec[i] = multiplier * eoq_q
        else:
            planned_rec[i] = 0
        
        end_inv[i] = beg_inv[i] + planned_rec[i] - gross_req[i]
        current_inv = end_inv[i]

    # Logika Lead Time (Plan Release di P-1)
    for i in range(1, 7):
        if planned_rec[i] > 0 and i - lead_time >= 0:
            planned_rel[i - lead_time] = planned_rec[i]

    # --- 5. PERHITUNGAN BIAYA ---
    # Setup Cost: dihitung dari berapa periode kita melakukan Release
    num_orders = sum(1 for x in planned_rel if x > 0)
    total_setup_cost = num_orders * cost_per_order
    
    # Holding Cost: sisa stok setiap akhir periode P1-P6
    total_inventory_held = sum(end_inv[1:])
    total_holding_cost = total_inventory_held * holding_cost_per_unit
    
    total_cost = total_setup_cost + total_holding_cost

    # --- 6. DISPLAY TABEL & BIAYA ---
    data = {
        "Gross Req": gross_req,
        "Beg. Inv": [0] + beg_inv[1:],
        "Plan Rec.": planned_rec,
        "End. Inv": [initial_inventory] + end_inv[1:],
        "Plan Rel.": planned_rel
    }
    
    df = pd.DataFrame(data, index=periods).T
    
    title = "MRP EOQ MULTIPLIER (HEIZER-RENDER) + SAFETY STOCK"
    cost_text = "Total Cost: " + str(total_cost) + " (Setup: " + str(total_setup_cost) + ", Holding: " + str(total_holding_cost) + ")"
    
    print("=" * 85)
    print(title.center(85))
    print("=" * 85)
    print(df.to_string())
    print("-" * 85)
    print(cost_text.center(85))
    print("=" * 85)

if __name__ == "__main__":
    generate_mrp_final_full()
