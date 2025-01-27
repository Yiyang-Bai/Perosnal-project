import Agently
from pyarrow import nulls
from statsmodels.graphics.tukeyplot import results

from sql import generate_sql, execute_sql
from datetime import date
from crawl import get_content

report_agent = (
    Agently.create_agent()
    .set_settings("current_model", "OAIClient")
        .set_settings("model.OAIClient.auth.api_key", "sk-e6f6e734fe964bc3a2f3f06523de5f98")
        .set_settings("model.OAIClient.url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        .set_settings("model.OAIClient.options.model", "qwen-turbo")
)


def create_report(user_id, company_name,number_of_news, agent):


    work_flow = Agently.Workflow()
    '''
    Agently.Workflow.public_storage.set("company_name", company_name)
    Agently.Workflow.public_storage.set("user_id", user_id)
    Agently.Workflow.public_storage.set("number_of_news", number_of_news)
    '''




    @work_flow.chunk()
    def generate_record(inputs,storage):
        request = (f"I need to insert a new record with user_id ={user_id},generate data ={date.today()}"
                   f"company_name={company_name},number_of_news={number_of_news},record_id is auto_increment")

        sql_sentence = generate_sql(request)
        print(f"insert:{sql_sentence}")
        execute_sql(sql_sentence)

        record_id_select = (f"I need to select record id from table record which company name is  {company_name},userid ={user_id}, generate data ={date.today()},"
                            f"number_of_news={number_of_news}")

        record_id_select_sql = generate_sql(record_id_select)


        print(f"select sentence:{record_id_select_sql}")
        record_id = execute_sql(record_id_select_sql)
        record_id = record_id[0][0]
        print(record_id)

        #Agently.Workflow.public_storage.set("Record_id", record_id)
        storage.set("record_id", record_id)

        return {"record_id" :record_id}


    @work_flow.chunk()
    def craw_news(inputs,storage):
        get_content(company_name, number_of_news, storage.get("record_id"))

        return number_of_news

    @work_flow.chunk()
    def select_news_generate_report(inputs,storage):
        request = f"I need you to generate a sql sentence that select all the news with this record_id {storage.get('record_id')}"
        sql_news_sentence = generate_sql(request)
        print(f"insert_news:{sql_news_sentence}")
        content = execute_sql(sql_news_sentence)
        print(execute_sql(sql_news_sentence))
        #content.replace("HTML_TAG_START", "").replace("HTML_TAG_END", "").strip()
        formatted_data = [
            {
                "news_ID": item[0],
                "record_ID": item[1],
                "URL": item[2],
                "Content": (item[3])#.replace("HTML_TAG_START", "").replace("HTML_TAG_END", "").strip()
            }
            for item in content

        ]
        #print(formatted_data)
        Cot_prompt = """
        You are an expert financial analyst tasked with creating a comprehensive research report on an investment bank. Follow these steps to systematically evaluate the bank’s performance, market position, and investment potential based on recent news, financial metrics, and industry context. Use the structure provided to generate a logical and detailed report.

        ### Step-by-Step Analysis

        1. **Executive Summary**:
           - Summarize the investment bank’s overall business, recent developments, and investment recommendation.
           - Provide a concise one-sentence recommendation (Hold, Buy, or Sell) with supporting rationale.
           - Highlight any notable strengths, challenges, and market positioning.

        2. **Company Overview**:
           - General Background:
             - Year of establishment, headquarters location, and key business segments.
             - Overview of the bank's mission and strategic focus.
           - Business Model:
             - Breakdown of primary revenue streams (e.g., Institutional Securities, Wealth Management, Asset Management, or Trading).
             - Highlight any unique differentiators (e.g., global reach, specialized services, digital transformation).

        3. **Recent News Analysis**:
           - Key Developments:
             - Summarize recent events or announcements (e.g., earnings results, strategic partnerships, regulatory changes, or market impacts).
             - Highlight news with direct implications for the bank’s financial health, reputation, or market positioning.
           - Market Reaction:
             - Explain how the news influenced stock price, trading volume, or analyst sentiment.
             - Compare the bank’s reaction to sector-wide trends.

        4. **Industry and Competitive Landscape**:
           - Industry Context:
             - Describe the current state of the investment banking sector, including key challenges and opportunities (e.g., rising interest rates, regulatory pressures, or technological advancements).
           - Competitor Analysis:
             - Compare the bank to key competitors (e.g., Goldman Sachs, JPMorgan Chase, or UBS).
             - Highlight areas where the bank leads or lags, such as market share, profitability, or innovation.
           - Positioning:
             - Discuss how the bank’s strategic focus aligns with broader industry trends (e.g., ESG initiatives, fintech integration).

        5. **Financial Performance Analysis**:
           - Key Metrics:
             - Analyze financial indicators using recent data:
               - Valuation: Price-to-Book ratio, PEG ratio, and comparison to industry peers.
               - Growth: EPS growth rates, revenue trends, and expansion opportunities.
               - Profitability: Net income, operating margins, and efficiency ratios (e.g., return on equity).
               - Momentum: Stock price performance relative to the sector.
               - Revisions: Recent EPS or revenue forecast changes from analysts.
           - Insights:
             - Highlight strengths or red flags in the financial performance.

        6. **Strategic Strengths and Risks**:
           - Strengths:
             - Identify areas of excellence, such as strong capital markets performance, successful wealth management growth, or innovative technology adoption.
           - Risks:
             - Discuss potential headwinds, such as economic volatility, geopolitical risks, regulatory scrutiny, or sector-wide challenges.

        7. **Opportunities for Growth**:
           - Identify emerging opportunities, such as:
             - Expanding into new markets or client segments.
             - Leveraging technology to enhance operational efficiency or customer experience.
             - Capitalizing on macroeconomic trends like higher interest rates or increased M&A activity.

        8. **Future Outlook**:
           - Predict how the bank is positioned for the next 6–12 months based on:
             - Recent developments, financial metrics, and industry conditions.
             - Its ability to address risks and capitalize on strengths.
           - Highlight potential catalysts that may improve (or hinder) performance.

        9. **Investment Recommendation**:
           - Provide a clear and concise recommendation (Hold, Buy, or Sell).
           - Justify the recommendation by weighing:
             - Recent news and market sentiment.
             - Financial performance.
             - Industry positioning and risks.
           - Summarize whether the bank is overvalued, fairly valued, or undervalued relative to its peers.

        ### Additional Instructions:
        - Use a formal and professional tone.
        - Ensure each section logically builds on the previous one.
        - Incorporate data points and references to recent events where applicable.
        - Conclude with actionable insights for investors.
        """
        report_result = (
            agent
            .general("you need to use the cot_prmpt to fo the right formate and news to generate report")
            .user_info("You are an expert financial analyst tasked with creating a comprehensive research report on an investment bank. "
                       "Follow these steps to systematically evaluate the bank’s performance, market position, "
                       "and investment potential based on recent news, financial metrics, and industry context. "
                       "Use the structure provided to generate a logical and detailed report.")
            .info(f"the research report need to floow this formate and steps :{Cot_prompt}， I need you to have all the content in this prompt, I need a long and specific report")
            .info(f"you als need to use these new to analyze the recent change to this company, these news is very important for this report{formatted_data}")
            .instruct(f"after you generate a report, use {Cot_prompt} to check if the report fellow the instruction, if not, change the missing or bad part untill it passed")
            .instruct(f"You are an expert financial analyst tasked with creating a comprehensive research report for a company. The report must include the following sections to ensure clarity and completeness:"
                      f"Summary:Purpose: Briefly summarize the key points of the report.Goal: Quickly convey the core arguments, including the company's opportunities and risks."
                      f"Investment Thesis:Purpose: Explain the primary reasons for recommending investment or highlighting risks.Goal: Understand the analyst's main reasoning and overall viewpoint."
                      f"Financial Performance:Purpose: Discuss recent financial data, including revenue, profit margins, and other key financial metrics.Goal: Assess the company’s current financial health and profitability trends."
                      f"Growth Drivers:Purpose: Analyze factors that may drive the company’s future growth, such as market trends, technological innovations, or acquisitions.Goal: Evaluate the sustainability of the company’s growth and its competitive edge."
                      f"Market Environment:Purpose: Provide background on macroeconomic, industry trends, or regulatory changes.Goal: Understand external factors influencing the company's performance."
                      f"Technological/Operational Highlights:Purpose: Focus on the company’s technological innovations (e.g., AI integration) or operational strategies for efficiency.Goal: Assess whether the company can enhance its competitiveness through technology or process improvements."
                      f"Valuation and Metrics:Purpose: Include valuation metrics (e.g., P/E ratio, PEG, P/S) and compare them to industry benchmarks or competitors.Goal: Determine whether the stock is overvalued, undervalued, or fairly priced."
                      f"Risk Analysis:Purpose: Highlight internal and external risks the company faces (e.g., regulatory changes, economic environment, or market competition).Goal: Identify potential issues that may impact the company’s performance."
                      f"Conclusion/Bottom Line:Purpose: Summarize the report’s key content and provide a final recommendation (e.g., Buy, Sell, or Hold).Goal: Reinforce the report's overall attitude toward the company"
                      f"Disclosure:Purpose: State whether the author has financial interests or other potential biases regarding the company.Goal: Evaluate any potential conflicts of interest in the author’s views."
                      f"Recent important news: to give some brif intoduction for recent news, and how can those news influence the market")
            .instruct("the report must more than 2000 words, the report must more than 2000 words")
            .output(f"Generate a syntactically correct SQL INSERT statement for MySQL. Ensure the following"
                    f"Escape all single quotes (') in the content by doubling them ('')."
                    f"Ensure the content is enclosed in single quotes."
                    f"The SQL statement should include a semicolon (;) at the end."
                    f"Do not include any explanations or additional output—return only the complete SQL query."
                    f"Example Input: Record ID: 10"
                    f"Report Content: Morgan Stanley's strong performance suggests a positive outlook."
                    f"example: INSERT INTO RESULT (Record_id, report_content) VALUES (10, 'Morgan Stanley''s strong performance suggests a positive outlook.');"
                    )



            .start()





)
        storage.set("research_report", report_result)



        return

    @work_flow.chunk()
    def insert_report(inputs, storage):
        sanitized_report = storage.get('research_report').replace("'", "''")

        request = (
            f"I need you to generate a SQL INSERT statement for MySQL to insert the following data:\n"
            f"Record ID: {storage.get('record_id')}\n"
            f"Report Content: {sanitized_report}\n"
            f"Ensure the following:\n"
            f"- All single quotes (') in the text are escaped by doubling them ('').\n"
            f"- Double quotes (\") do not require escaping.\n"
            f"- The SQL statement is properly formatted and ends with a semicolon (;).\n"
            f"- Return only the corrected SQL query without any explanations."
        )

        final_report = generate_sql(request)

        print(f"Generated SQL Query: {final_report}")

        execute_sql(final_report)
        print(storage.get('research_report'))

        return storage.get("research_report")

    (

        work_flow
    .connect_to("generate_record")
    .connect_to("craw_news")
    .connect_to("select_news_generate_report")
    .connect_to("insert_report")
    .connect_to("END")
    )

    work_flow.start()



    return generate_record

