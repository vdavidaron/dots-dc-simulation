<?xml version='1.0' encoding='UTF-8'?>
<esdl:EnergySystem xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:esdl="http://www.tno.nl/esdl" name="Datacenter_BESS_Scenario" id="0e6435d4-b36b-4529-88c4-f3532fae6c4a" description="Datacenter with BESS and grid connection">
  <instance xsi:type="esdl:Instance" name="scenario_instance" id="86170fab-2678-460e-b728-383b22b7fd55">
    <area xsi:type="esdl:Area" name="Datacenter_Site" id="a5f40862-b87a-4b84-9dc3-0be8ebbedc45">
      <asset xsi:type="esdl:ElectricityNetwork" id="f15c3bcd-2afb-4d5d-a2cf-938d686d1a9d" name="Site Electricity Management System">
        <port xsi:type="esdl:OutPort" name="net_to_datacenter" id="6b2a15f1-a780-4dc4-9fcf-0b7c60e55ea7" connectedTo="b8492d50-0ed4-4499-a59f-6b99bc2172d5"/>
        <port xsi:type="esdl:OutPort" name="net_to_bess" id="643fac94-fad1-4403-932b-a02cdaa0cea2" connectedTo="5c4ae837-a721-44d7-a264-302c23bd5456"/>
        <port xsi:type="esdl:InPort" name="net_from_bess" id="7601b6ab-bf0a-413b-bf72-93e824919870" connectedTo="b59e3188-20cd-4922-949c-adeb2b97c9c8"/>
        <port xsi:type="esdl:OutPort" name="net_to_grid" id="0fa083f0-d193-4d15-93d3-9408ebd296f4" connectedTo="bc918d72-2e12-488a-9c36-3548a9ce53a1"/>
        <port xsi:type="esdl:InPort" name="net_from_grid" id="7ea6aa3f-fbc7-4628-a3f5-aaa1c88a0934" connectedTo="b87f2512-d237-4778-8df0-31602d418453"/>
        <port xsi:type="esdl:InPort" name="net_from_backup_generator" id="18e2bea9-fec8-4476-9a42-e41ebeebb076" connectedTo="315c6dd3-365d-492d-9d81-e95ccb326750"/>
        <port xsi:type="esdl:InPort" name="net_from_local_res" id="c72f5ccf-11db-49f8-8d50-d40783d60fd5" connectedTo="5d3976e4-8dba-4199-9cc1-e32032314726"/>
        <KPIs xsi:type="esdl:KPIs" id="338cd00c-ba44-4053-9924-ae081ad445cf">
          <kpi xsi:type="esdl:DoubleKPI" name="w_unserved" value="1000000000.0" id="e1549126-9dc4-4a1d-ab4c-16097116fcde"/>
          <kpi xsi:type="esdl:DoubleKPI" name="w_carbon" value="1.0" id="fcda82f3-e83f-44c0-a5c4-4b76940b6ae0"/>
          <kpi xsi:type="esdl:DoubleKPI" name="w_price" value="1.0" id="b69d5a98-3bfe-4d0a-b139-d4eea8c47e25"/>
          <kpi xsi:type="esdl:DoubleKPI" name="w_effort" value="0.01" id="e46b6e0d-5f1c-4df0-a311-1f01c7b621bd"/>
          <kpi xsi:type="esdl:DoubleKPI" name="w_soc_low" value="1000000.0" id="7c2d9293-1909-4b45-a78d-1c26c8550fc6"/>
          <kpi xsi:type="esdl:DoubleKPI" name="soc_baseline" value="50.0" id="8457ce1d-fb28-4f4d-a3c5-f366613c95fb"/>
          <kpi xsi:type="esdl:DoubleKPI" name="enable_battery" value="1.0" id="9c4a2992-31c9-45d7-9a48-0ae2664b8e7d"/>
          <kpi xsi:type="esdl:DoubleKPI" name="enable_backup_generator" value="1.0" id="fe3c9ca3-49ca-446b-a082-185dede70728"/>
          <kpi xsi:type="esdl:DoubleKPI" name="enable_renewable_service" value="1.0" id="0c65a43a-15f7-41b1-8927-a54c3ad9587d"/>
          <kpi xsi:type="esdl:DoubleKPI" name="enable_change_management" value="1.0" id="f74121a9-090d-490d-a239-c97c52be1bcc"/>
          <kpi xsi:type="esdl:DoubleKPI" name="enable_goal_management" value="1.0" id="f297ecaf-5e69-4c5b-8bfb-a3531c4fd9c9"/>
          <kpi xsi:type="esdl:DoubleKPI" name="enable_mandate" value="1.0" id="a380c030-3e22-48b9-aad2-d0d8eee96967"/>
          <kpi xsi:type="esdl:DoubleKPI" name="mpc_soc_drift_threshold" value="5.0" id="35df33e5-a99d-4faa-8238-1f344beda1d6"/>
          <kpi xsi:type="esdl:DoubleKPI" name="mpc_demand_spike_threshold" value="0.1" id="2be9f7cd-bc22-483d-bdad-69446f0aad0d"/>
          <kpi xsi:type="esdl:DoubleKPI" name="mpc_horizon_steps" value="24.0" id="b757ff9f-9844-4798-b47a-d83e2421f9a3"/>
          <kpi xsi:type="esdl:DoubleKPI" name="mpc_replan_cooldown" value="4.0" id="c53d8a9a-05b0-4f4d-bc14-da2c69371e02"/>
          <kpi xsi:type="esdl:DoubleKPI" name="forecast_sigma_ci" value="0.12" id="ceeb96e8-3dfe-472a-bc63-ac4ddc2113db"/>
          <kpi xsi:type="esdl:DoubleKPI" name="forecast_sigma_p_dc" value="0.05" id="71119e59-a36a-46d2-8885-e404bd836f0d"/>
          <kpi xsi:type="esdl:DoubleKPI" name="forecast_sigma_price" value="0.15" id="3a34d533-69b0-4815-9076-b91e444ecd5f"/>
          <kpi xsi:type="esdl:DoubleKPI" name="forecast_seed" value="42.0" id="30a05c17-309f-4506-af87-26e8779fc793"/>
          <kpi xsi:type="esdl:DoubleKPI" name="backup_co2_factor" value="600.0" id="877e6840-d9f3-452c-852f-991e232c5327"/>
          <kpi xsi:type="esdl:DoubleKPI" name="backup_cost_eur_per_kwh" value="0.4" id="94fc82af-2ea6-4efe-ad8f-1e98399b9cc0"/>
          <kpi xsi:type="esdl:DoubleKPI" name="sim_seed" value="42.0" id="5f6c4b33-afbc-4f3f-aa99-c82358588019"/>
        </KPIs>
      </asset>
      <asset xsi:type="esdl:ElectricityDemand" powerFactor="0.95" id="59cf3128-4f09-40d5-a680-984ee5a04166" power="4000000.0" name="Datacenter Load">
        <port xsi:type="esdl:InPort" name="dc_in" connectedTo="6b2a15f1-a780-4dc4-9fcf-0b7c60e55ea7" id="b8492d50-0ed4-4499-a59f-6b99bc2172d5">
          <profile xsi:type="esdl:InfluxDBProfile" host="influxdb" filters="name='Datacenter Load'" measurement="historical_datacenter_demand" port="8086" field="Demand_W" database="GO-e" id="dfd4ab8d-9f47-4f7d-be6d-3f4cb4b4e69e"/>
        </port>
      </asset>
      <asset xsi:type="esdl:Battery" chargeEfficiency="0.95" capacity="4000000.0" id="fa7eed46-7627-4e70-8628-576163f878d1" maxDischargeRate="4000000.0" maxChargeRate="4000000.0" dischargeEfficiency="0.95" name="Datacenter BESS">
        <port xsi:type="esdl:InPort" name="bess_in" id="5c4ae837-a721-44d7-a264-302c23bd5456" connectedTo="643fac94-fad1-4403-932b-a02cdaa0cea2"/>
        <port xsi:type="esdl:OutPort" name="bess_out" id="b59e3188-20cd-4922-949c-adeb2b97c9c8" connectedTo="7601b6ab-bf0a-413b-bf72-93e824919870"/>
      </asset>
      <asset xsi:type="esdl:PowerPlant" power="10000000.0" id="ff1140f9-16a0-4aea-a45f-5202f4f19d2b" efficiency="1.0" name="Grid Connection" minLoad="-10000000">
        <port xsi:type="esdl:InPort" name="grid_in" connectedTo="0fa083f0-d193-4d15-93d3-9408ebd296f4" id="bc918d72-2e12-488a-9c36-3548a9ce53a1">
          <profile xsi:type="esdl:InfluxDBProfile" host="influxdb" filters="name='Grid Connection'" measurement="transformer_background" port="8086" field="background_w" database="GO-e" id="d7b56972-7d52-42d3-81de-60e385a2d5cb"/>
          <profile xsi:type="esdl:InfluxDBProfile" host="influxdb" filters="name='Grid Connection'" measurement="carbon_intensity" port="8086" field="carbon_intensity" database="GO-e" id="06c3c925-b43f-4b19-b012-558b22b3e927"/>
          <profile xsi:type="esdl:InfluxDBProfile" host="influxdb" filters="name='Grid Connection'" measurement="price-day-ahead" port="8086" field="price" database="GO-e" id="da7e880a-9f65-4f5c-b8d6-77ab10561484"/>
        </port>
        <port xsi:type="esdl:OutPort" name="grid_out" id="b87f2512-d237-4778-8df0-31602d418453" connectedTo="7ea6aa3f-fbc7-4628-a3f5-aaa1c88a0934"/>
      </asset>
      <asset xsi:type="esdl:GasProducer" id="df16647e-c554-4bb5-ac66-0de81a547471" power="5000000.0" name="Backup Generator">
        <port xsi:type="esdl:OutPort" name="gen_out" id="315c6dd3-365d-492d-9d81-e95ccb326750" connectedTo="18e2bea9-fec8-4476-9a42-e41ebeebb076"/>
      </asset>
      <asset xsi:type="esdl:PVInstallation" angle="35" panelEfficiency="0.2" id="cda0da95-a1d6-4b85-a7b7-6a862810c07e" power="1000000.0" orientation="180" inverterEfficiency="0.98" surfaceArea="5000" name="Local Renewable Energy Source">
        <port xsi:type="esdl:OutPort" connectedTo="c72f5ccf-11db-49f8-8d50-d40783d60fd5" name="res_out" id="5d3976e4-8dba-4199-9cc1-e32032314726">
          <profile xsi:type="esdl:InfluxDBProfile" host="influxdb" filters="name='Local RES'" measurement="historical_solar_irradiance" port="8086" field="Irradiance_W_m2" database="GO-e" id="9c83f280-b07e-440d-9eac-7c2a797c7305"/>
        </port>
      </asset>
    </area>
  </instance>
</esdl:EnergySystem>
