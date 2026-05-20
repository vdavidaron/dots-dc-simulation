# dots-dc-simulation
Starting simulation for dots dc calculation services

needed:
kubectl, kind

run: https://github.com/dots-energy/dots-simulation-orchestrator.git

The math behind transformer constraints. 
Let $B_t$ be the background demand and $D_t$ be the datacenter load at hour $t$:

Upper Limit: $B_t + D_t \le 90$. If the datacenter exceeds this, it trips the transformer (capacity drops to 0). So, the maximum allowed load is $90 - B_t$. 

Lower Limit: $B_t + D_t \ge -90$. If there is a massive overproduction of renewables pushing the background past -90, the datacenter must soak up the excess. The minimum required load is $-90 - B_t$. (the more soaked up energy, the lower the energy price)