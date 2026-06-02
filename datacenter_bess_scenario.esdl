<?xml version='1.0' encoding='UTF-8'?>
<esdl:EnergySystem xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:esdl="http://www.tno.nl/esdl" id="fb3e1d17-807d-4c26-8392-611734663d0b" name="Datacenter_BESS_Scenario" description="Datacenter with BESS and grid connection">
  <instance xsi:type="esdl:Instance" name="scenario_instance" id="12dc6f8e-759c-468d-a7e7-5b94538c64b8">
    <area xsi:type="esdl:Area" name="Datacenter_Site" id="080d903d-8a1c-4652-81e0-79ca9eabf181">
      <asset xsi:type="esdl:ElectricityNetwork" id="ae810cbf-1a6f-4433-bbbf-9c17151343a0" name="Site Electricity Management System">
        <KPIs xsi:type="esdl:KPIs" id="18d4fc3c-0c42-4fe3-a06c-a2ecaa99a969">
          <kpi xsi:type="esdl:DoubleKPI" value="1000000000.0" id="2108fc03-1850-46df-8bf3-f4c4f35fbe0c" name="w_unserved"/>
          <kpi xsi:type="esdl:DoubleKPI" value="1.0" id="db96af64-89b2-4286-95e3-ebc48ddc0966" name="w_carbon"/>
          <kpi xsi:type="esdl:DoubleKPI" value="1.0" id="d7862d1a-9bea-4979-b904-3cbe9fb0ae4f" name="w_price"/>
          <kpi xsi:type="esdl:DoubleKPI" value="0.01" id="7660026a-c028-4283-a93e-9803054d693b" name="w_effort"/>
          <kpi xsi:type="esdl:DoubleKPI" value="1000000.0" id="d3bcbc7e-f219-4e41-9177-ddf042139341" name="w_soc_low"/>
          <kpi xsi:type="esdl:DoubleKPI" value="50.0" id="fd7de5b3-fab6-4e00-95ac-f9f067cf69f0" name="soc_baseline"/>
          <kpi xsi:type="esdl:DoubleKPI" value="1.0" id="66397d44-33d4-4823-88b5-df8de3c81297" name="enable_battery"/>
          <kpi xsi:type="esdl:DoubleKPI" value="1.0" id="894cf9e6-322b-4827-93e8-f75319364ced" name="enable_backup_generator"/>
          <kpi xsi:type="esdl:DoubleKPI" value="1.0" id="2c0474ea-636b-4031-bc36-b8628952ab77" name="enable_renewable_service"/>
          <kpi xsi:type="esdl:DoubleKPI" value="1.0" id="dcba63a6-eac2-4807-b46b-d38a656575fd" name="enable_change_management"/>
          <kpi xsi:type="esdl:DoubleKPI" value="1.0" id="23c1310a-3b02-4aaf-863a-48b9b76083ae" name="enable_goal_management"/>
          <kpi xsi:type="esdl:DoubleKPI" value="1.0" id="822d266a-c65f-4d38-a96f-4d7929110c2e" name="enable_mandate"/>
          <kpi xsi:type="esdl:DoubleKPI" value="5.0" id="170236f2-aa94-41c4-9799-ef6024dc8a41" name="mpc_soc_drift_threshold"/>
          <kpi xsi:type="esdl:DoubleKPI" value="0.1" id="9c0c9e0a-a463-44e3-ac91-2d5c4b04736d" name="mpc_demand_spike_threshold"/>
          <kpi xsi:type="esdl:DoubleKPI" value="24.0" id="9dbf7d1e-648e-42bb-97dd-5f2d4d9138f8" name="mpc_horizon_steps"/>
          <kpi xsi:type="esdl:DoubleKPI" value="4.0" id="40abc45a-e5ae-4afe-888d-82123f4e4e61" name="mpc_replan_cooldown"/>
          <kpi xsi:type="esdl:DoubleKPI" value="0.12" id="68a050ce-bb31-4b68-bd3f-5ab888712e84" name="forecast_sigma_ci"/>
          <kpi xsi:type="esdl:DoubleKPI" value="0.05" id="e83a0e02-4de1-4099-a322-414668905ca4" name="forecast_sigma_p_dc"/>
          <kpi xsi:type="esdl:DoubleKPI" value="0.15" id="cdcdd5b3-c9dd-40ae-98a2-5136b31e6cca" name="forecast_sigma_price"/>
          <kpi xsi:type="esdl:DoubleKPI" value="42.0" id="0a5e8804-5e38-4311-9847-13eabd905a45" name="forecast_seed"/>
          <kpi xsi:type="esdl:DoubleKPI" value="600.0" id="f7a2f5b4-0721-4d42-a0cc-c5fd74dd76df" name="backup_co2_factor"/>
          <kpi xsi:type="esdl:DoubleKPI" value="0.4" id="1b332207-8798-49b2-8dba-ba432eee00df" name="backup_cost_eur_per_kwh"/>
        </KPIs>
        <port xsi:type="esdl:OutPort" connectedTo="4ede5cae-96ae-4936-bb0f-13810259cc6b" name="net_to_datacenter" id="5788f82e-ecc8-4cc9-9546-a4a474efdea3"/>
        <port xsi:type="esdl:OutPort" connectedTo="cc571622-20be-45ef-b754-1348269ebfe7" name="net_to_bess" id="7ba583e0-87ec-4cd6-b828-ac92c742711f"/>
        <port xsi:type="esdl:InPort" name="net_from_bess" id="23fd30db-df11-407f-a2f5-c6af55b2dede" connectedTo="50794999-6cb7-426e-83c1-31edb4ba58db"/>
        <port xsi:type="esdl:OutPort" connectedTo="c9a74e79-7f7c-40d5-ae4d-edba48d8e354" name="net_to_grid" id="77492664-6a8d-4731-8570-ad0ebdbc4d55"/>
        <port xsi:type="esdl:InPort" name="net_from_grid" id="a960eb08-3d88-4097-8b6c-5e2f25cb12de" connectedTo="6cca0002-9c0a-45e8-b1c2-e34f4f94d795"/>
        <port xsi:type="esdl:InPort" name="net_from_backup_generator" id="7ebdb83d-7bdb-4a57-a172-807fe53752be" connectedTo="06cd5dbf-dcc6-4576-928f-a578bc0017cf"/>
        <port xsi:type="esdl:InPort" name="net_from_local_res" id="083aafef-6a9e-4a1c-bec6-5f4d68af6d46" connectedTo="5d247ed6-922b-4dd8-8150-15cb5763202c"/>
      </asset>
      <asset xsi:type="esdl:ElectricityDemand" power="4000000.0" id="da5b37d6-5a64-4458-be0c-2db823709cb5" name="Datacenter Load" powerFactor="0.95">
        <port xsi:type="esdl:InPort" name="dc_in" connectedTo="5788f82e-ecc8-4cc9-9546-a4a474efdea3" id="4ede5cae-96ae-4936-bb0f-13810259cc6b">
          <profile xsi:type="esdl:InfluxDBProfile" id="dee06003-920e-43a7-b5a5-d1aab137c5d1" database="GO-e" measurement="historical_datacenter_demand" field="Demand_W" host="influxdb" filters="name='Datacenter Load'" port="8086"/>
        </port>
      </asset>
      <asset xsi:type="esdl:Battery" maxDischargeRate="4000000.0" maxChargeRate="4000000.0" id="7640b306-3d1d-449f-92b4-cb5b7919055a" dischargeEfficiency="0.95" chargeEfficiency="0.95" capacity="4000000.0" name="Datacenter BESS">
        <port xsi:type="esdl:InPort" name="bess_in" id="cc571622-20be-45ef-b754-1348269ebfe7" connectedTo="7ba583e0-87ec-4cd6-b828-ac92c742711f"/>
        <port xsi:type="esdl:OutPort" connectedTo="23fd30db-df11-407f-a2f5-c6af55b2dede" name="bess_out" id="50794999-6cb7-426e-83c1-31edb4ba58db"/>
      </asset>
      <asset xsi:type="esdl:PowerPlant" efficiency="1.0" id="71824ecc-7404-4e5d-a93f-2dc1f6ab8023" minLoad="-10000000" power="10000000.0" name="Grid Connection">
        <port xsi:type="esdl:InPort" name="grid_in" connectedTo="77492664-6a8d-4731-8570-ad0ebdbc4d55" id="c9a74e79-7f7c-40d5-ae4d-edba48d8e354">
          <profile xsi:type="esdl:InfluxDBProfile" id="67b05bd2-8685-4ba0-b66d-f76d3890c384" database="GO-e" measurement="transformer_background" field="background_w" host="influxdb" filters="name='Grid Connection'" port="8086"/>
          <profile xsi:type="esdl:InfluxDBProfile" id="40af61a8-cf14-4a50-ac0c-f073392fa151" database="GO-e" measurement="carbon_intensity" field="carbon_intensity" host="influxdb" filters="name='Grid Connection'" port="8086"/>
          <profile xsi:type="esdl:InfluxDBProfile" id="7fa62c0c-11b7-4cd9-bb98-432b039d5322" database="GO-e" measurement="price-day-ahead" field="price" host="influxdb" filters="name='Grid Connection'" port="8086"/>
        </port>
        <port xsi:type="esdl:OutPort" connectedTo="a960eb08-3d88-4097-8b6c-5e2f25cb12de" name="grid_out" id="6cca0002-9c0a-45e8-b1c2-e34f4f94d795"/>
      </asset>
      <asset xsi:type="esdl:GasProducer" power="5000000.0" id="3d8a58ab-5f14-49e7-8006-3e566e04e070" name="Backup Generator">
        <port xsi:type="esdl:OutPort" connectedTo="7ebdb83d-7bdb-4a57-a172-807fe53752be" name="gen_out" id="06cd5dbf-dcc6-4576-928f-a578bc0017cf"/>
      </asset>
      <asset xsi:type="esdl:PVInstallation" panelEfficiency="0.2" power="1000000.0" id="92d93e8d-c14d-4223-bb1b-652f1f1f3d29" surfaceArea="5000" orientation="180" inverterEfficiency="0.98" angle="35" name="Local Renewable Energy Source">
        <port xsi:type="esdl:OutPort" name="res_out" connectedTo="083aafef-6a9e-4a1c-bec6-5f4d68af6d46" id="5d247ed6-922b-4dd8-8150-15cb5763202c">
          <profile xsi:type="esdl:InfluxDBProfile" id="22fc3d6b-06e3-4531-a7fa-e6fb0ace6d24" database="GO-e" measurement="historical_solar_irradiance" field="Irradiance_W_m2" host="influxdb" filters="name='Local RES'" port="8086"/>
        </port>
      </asset>
    </area>
  </instance>
</esdl:EnergySystem>
