# Analyze with Azure Data Fabric

## Prerequisites
1. Completed step 5 of this tutorial, **Setup Streaming to Azure**.

## Steps to Complete


1. Create Fabric Gateway Connection to Azure IoT Hub (or Event Hub) by completing the steps in [Data Factory Data Source Management](https://learn.microsoft.com/en-us/fabric/data-factory/data-source-management).  You will use the SAS token created in the previous section (Stream to Azure).

2. [Create a KQL database](https://learn.microsoft.com/en-us/fabric/real-time-analytics/create-database).

3. [Setup EventStream](https://learn.microsoft.com/en-us/fabric/real-time-analytics/event-streams/create-manage-an-eventstream)

4. [Configure EventStream Source](https://learn.microsoft.com/en-us/fabric/real-time-analytics/event-streams/create-manage-an-eventstream) source for the Azure IoT Hub (or Event Hub) created in previous section (Stream to Azure).

5. [Configure EventStream Destination](https://learn.microsoft.com/en-us/fabric/real-time-analytics/event-streams/add-manage-eventstream-destinations) to the KQL Database created in step 2.

6. [Create KQL Queryset](https://learn.microsoft.com/en-us/fabric/real-time-analytics/kusto-query-set) using the query provided in this repo: [KQL Queryset Sample.txt](KQL_Queryset_Sample.txt).

7. Create a Power BI report from the KQL Queryset following the steps in [Visalize data in a PowerBI Report](https://learn.microsoft.com/en-us/fabric/real-time-analytics/create-powerbi-report).

8. Use Power BI Copilot to assist in report creation using natural language.  Please see [Overview of Copilot for Power BI](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-introduction) and [Microsoft Power BI Blog](https://powerbi.microsoft.com/en-us/blog/empower-power-bi-users-with-microsoft-fabric-and-copilot/) for guidance.

**NOTE:** The Copilot public preview is being rolled out in stages.  Initially, it will require Fabric capacity of F64 or higher or Power BI Premium capacity (P1 or higher).  

