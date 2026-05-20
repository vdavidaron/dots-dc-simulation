<?xml version='1.0' encoding='UTF-8'?>
<esdl:EnergySystem xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:esdl="http://www.tno.nl/esdl" name="Datacenter_BESS_Scenario" description="Datacenter with BESS and grid connection" id="daec1407-a297-4cb3-961f-4ba4ffbf7b67">
  <instance xsi:type="esdl:Instance" name="scenario_instance" id="f28c44f9-d3db-4d87-87ea-1b22f0bc152e">
    <area xsi:type="esdl:Area" name="Datacenter_Site" id="00c1721a-546a-4eee-9596-f6c2da307b5c">
      <asset xsi:type="esdl:ElectricityNetwork" id="12a85884-089a-4703-91ec-1bfb354d2203" name="Site Electricity Management System">
        <port xsi:type="esdl:OutPort" name="net_to_datacenter" connectedTo="80634b16-6de6-4f7d-b3fa-b784cc37075a" id="be192bc6-ad18-49b1-8bd2-19643a272da6"/>
        <port xsi:type="esdl:OutPort" name="net_to_bess" connectedTo="8f958780-7963-4845-8d7a-81eb90afbe4c" id="3d8628f4-904f-43b5-a253-96732afb23bb"/>
        <port xsi:type="esdl:InPort" name="net_from_bess" connectedTo="4467b37e-8895-417e-984b-760f372af05e" id="67aa99eb-db93-4d15-b6ee-7d656349c935"/>
        <port xsi:type="esdl:OutPort" name="net_to_grid" connectedTo="fa10fbc6-fb7f-42fe-b71e-445ce125e9e7" id="10abd24e-9a99-481c-8ea1-9d3b55be6133"/>
        <port xsi:type="esdl:InPort" name="net_from_grid" connectedTo="38e2b27a-b06b-4c43-b787-0f99cdd0d88b" id="008839f4-6f73-4a91-b918-b110751e6f20"/>
        <port xsi:type="esdl:InPort" name="net_from_backup_generator" connectedTo="307aeff3-ee74-4ca2-a256-1f4ebaeea228" id="89e08e5b-26e5-4c66-ad9f-76464afcb9b5"/>
        <port xsi:type="esdl:InPort" name="net_from_local_res" connectedTo="be566210-c444-4ba6-8978-353190d41b1d" id="095fc72a-e14f-4781-ad1d-d3288e122902"/>
        <KPIs xsi:type="esdl:KPIs" id="2fc77dc6-2474-47d1-b594-28d02c3fff43">
          <kpi xsi:type="esdl:DoubleKPI" id="141a2556-e520-473c-b281-cfcf4869f827" name="w_unserved" value="1000000000.0"/>
          <kpi xsi:type="esdl:DoubleKPI" id="d9092b2a-1999-43a2-9790-82668c0db904" name="w_carbon" value="1.0"/>
          <kpi xsi:type="esdl:DoubleKPI" id="21de9d10-1d4f-456c-835a-62b12dd273ab" name="w_price" value="1.0"/>
          <kpi xsi:type="esdl:DoubleKPI" id="263b736d-4328-49ac-9a9e-5e8b0475e7dc" name="w_effort" value="0.01"/>
          <kpi xsi:type="esdl:DoubleKPI" id="1c3a0c21-ca89-4491-9fb7-4f879e2eb068" name="w_soc_low" value="1000000.0"/>
          <kpi xsi:type="esdl:DoubleKPI" id="ec234965-707d-480f-aee4-3a12797f6466" name="soc_baseline" value="50.0"/>
          <kpi xsi:type="esdl:DoubleKPI" id="77048f84-8cc6-4807-95b0-0140522fdeb9" name="enable_battery" value="1.0"/>
          <kpi xsi:type="esdl:DoubleKPI" id="8bd365c3-3735-46ef-99c3-7fbc8f16987b" name="enable_backup_generator" value="1.0"/>
          <kpi xsi:type="esdl:DoubleKPI" id="192a4909-5a33-413c-8d72-0cfc11ebe19e" name="enable_renewable_service" value="1.0"/>
          <kpi xsi:type="esdl:DoubleKPI" id="afdc0c44-48f9-481b-bf3f-c4bfa2590a0e" name="enable_change_management" value="1.0"/>
          <kpi xsi:type="esdl:DoubleKPI" id="0d89d077-783e-4866-9ee2-a5d8ab8c3217" name="enable_goal_management" value="1.0"/>
          <kpi xsi:type="esdl:DoubleKPI" id="2d4ca6d8-a9b2-4cad-910c-deaa8720a269" name="enable_mandate" value="1.0"/>
          <kpi xsi:type="esdl:DoubleKPI" id="be2c29d9-bda7-488e-bcac-b342c9ac8dbb" name="mpc_soc_drift_threshold" value="5.0"/>
          <kpi xsi:type="esdl:DoubleKPI" id="85eef7c4-680a-4548-a6db-c575a336ac4c" name="mpc_demand_spike_threshold" value="0.1"/>
          <kpi xsi:type="esdl:DoubleKPI" id="49da7439-4b0c-4873-8ae1-13c293bc07fd" name="mpc_horizon_steps" value="24.0"/>
          <kpi xsi:type="esdl:DoubleKPI" id="5a7d5121-4b0f-456c-9218-9b2c9366cf68" name="mpc_replan_cooldown" value="4.0"/>
          <kpi xsi:type="esdl:DoubleKPI" id="151201c4-1ec3-4036-af62-e65d522f4432" name="forecast_sigma_ci" value="0.12"/>
          <kpi xsi:type="esdl:DoubleKPI" id="f4ab2983-dda5-4059-9fd6-17614d4bfebd" name="forecast_sigma_p_dc" value="0.05"/>
          <kpi xsi:type="esdl:DoubleKPI" id="1c5b9ff4-b3b2-4e04-b5ff-1631d93f1a84" name="forecast_sigma_price" value="0.15"/>
          <kpi xsi:type="esdl:DoubleKPI" id="b67752e0-ab72-47ce-ab42-adb0362477f9" name="forecast_seed" value="42.0"/>
        </KPIs>
      </asset>
      <asset xsi:type="esdl:ElectricityDemand" id="5e3b7609-9368-498f-838f-9b5cdfc7d64b" powerFactor="0.95" name="Datacenter Load" power="4000000.0">
        <port xsi:type="esdl:InPort" name="dc_in" connectedTo="be192bc6-ad18-49b1-8bd2-19643a272da6" id="80634b16-6de6-4f7d-b3fa-b784cc37075a">
          <profile xsi:type="esdl:InfluxDBProfile" id="cd61a52f-b253-451f-82d4-6deecefbc75d" database="GO-e" host="influxdb" measurement="historical_datacenter_demand" filters="name='Datacenter Load'" port="8086" field="Demand_W"/>
        </port>
      </asset>
      <asset xsi:type="esdl:Battery" id="6f54964b-9609-4b82-b4b4-e12b367976b7" chargeEfficiency="0.95" capacity="4000000.0" maxDischargeRate="4000000.0" name="Datacenter BESS" maxChargeRate="4000000.0" dischargeEfficiency="0.95">
        <port xsi:type="esdl:InPort" name="bess_in" connectedTo="3d8628f4-904f-43b5-a253-96732afb23bb" id="8f958780-7963-4845-8d7a-81eb90afbe4c"/>
        <port xsi:type="esdl:OutPort" name="bess_out" connectedTo="67aa99eb-db93-4d15-b6ee-7d656349c935" id="4467b37e-8895-417e-984b-760f372af05e"/>
      </asset>
      <asset xsi:type="esdl:PowerPlant" id="5e36c49f-10ee-4c01-ba09-f47058e4e874" minLoad="-75000000" power="75000000.0" name="Grid Connection" efficiency="1.0">
        <port xsi:type="esdl:InPort" name="grid_in" connectedTo="10abd24e-9a99-481c-8ea1-9d3b55be6133" id="fa10fbc6-fb7f-42fe-b71e-445ce125e9e7">
          <profile xsi:type="esdl:InfluxDBProfile" id="d36e65f9-fbcf-4ead-a87a-307d517802cb" database="GO-e" host="influxdb" measurement="transformer_background" filters="name='Grid Connection'" port="8086" field="background_w"/>
          <profile xsi:type="esdl:InfluxDBProfile" id="3b1f63cf-0644-48ba-acde-2c6b2f321433" database="GO-e" host="influxdb" measurement="carbon_intensity" filters="name='Grid Connection'" port="8086" field="carbon_intensity"/>
          <profile xsi:type="esdl:InfluxDBProfile" id="788616d7-2209-4499-8aad-a2500005b2f6" database="GO-e" host="influxdb" measurement="price-day-ahead" filters="name='Grid Connection'" port="8086" field="price"/>
        </port>
        <port xsi:type="esdl:OutPort" name="grid_out" connectedTo="008839f4-6f73-4a91-b918-b110751e6f20" id="38e2b27a-b06b-4c43-b787-0f99cdd0d88b"/>
      </asset>
      <asset xsi:type="esdl:GasProducer" id="50b9292b-9430-4fef-993f-39db43005ec6" power="5000000.0" name="Backup Generator">
        <port xsi:type="esdl:OutPort" name="gen_out" connectedTo="89e08e5b-26e5-4c66-ad9f-76464afcb9b5" id="307aeff3-ee74-4ca2-a256-1f4ebaeea228"/>
      </asset>
      <asset xsi:type="esdl:PVInstallation" id="51765227-fc4d-40a7-9c01-6a153be9f2ab" angle="35" surfaceArea="5000" panelEfficiency="0.2" power="1000000.0" name="Local Renewable Energy Source" orientation="180" inverterEfficiency="0.98">
        <port xsi:type="esdl:OutPort" name="res_out" id="be566210-c444-4ba6-8978-353190d41b1d" connectedTo="095fc72a-e14f-4781-ad1d-d3288e122902">
          <profile xsi:type="esdl:InfluxDBProfile" id="af74a988-d4b5-4461-ad0e-c0e663fd761b" database="GO-e" host="influxdb" measurement="historical_solar_irradiance" filters="name='Local RES'" port="8086" field="Irradiance_W_m2"/>
        </port>
      </asset>
    </area>
  </instance>
</esdl:EnergySystem>
