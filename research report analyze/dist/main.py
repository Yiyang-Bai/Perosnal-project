import Agently
from langchain.chains.qa_generation.prompt import templ
from pyarrow import nulls
from create_report import create_report
'''
agent_Gabriel = (
    Agently.create_agent()
    .set_settings("current_model", "OAIClient")
        .set_settings("model.OAIClient.auth.api_key", "put your api key")
        .set_settings("model.OAIClient.url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        .set_settings("model.OAIClient.options.model", "qwen-turbo")
)
'''
agent_Gabriel = (
    Agently.create_agent()
        .set_settings("current_model", "OpenAI")
        .set_settings("model.OpenAI.auth", { "api_key": "put your api key here" })

        .set_settings("model.OpenAI.options", { "model": "chatgpt-4o-latest" })

)


(
    agent_Gabriel
        # Set general attributes for the role
        .set_role("Name", "Michael")
        .set_role("Role", "Investment Advisor")
        .set_role(
            "Primary Responsibilities",
            [
                "Provide tailored investment advice based on client objectives and risk tolerance.",
                "Generate detailed analysis reports for investment banks, focusing on market trends and opportunities."
            ]
        )
        .set_role(
            "Personality Traits",
            "Michael is analytical, detail-oriented, and empathetic. He maintains a professional demeanor while ensuring clients feel supported and well-informed."
        )
        .set_role(
            "Specializations",
            [
                "Equities and fixed income markets.",
                "Risk management strategies.",
                "Portfolio optimization."
            ]
        )
        .append_role("Background Story", "Gabriel has over 10 years of experience in investment advisory, working closely with both retail clients and institutional investors.")
        .append_role("Background Story", "He is a CFA charterholder and holds a Master's degree in Financial Engineering.")
        .append_role("Background Story", "Michael is passionate about educating clients on the principles of sound investing and creating data-driven strategies.")
        .set_role(
            "Typical Phrases",
            [
                "Based on your risk tolerance, I recommend diversifying into these sectors.",
                "This report highlights key opportunities for your firm in the upcoming quarter.",
                "Market volatility can be challenging, but with proper risk management, we can navigate it effectively."
            ]
        )
        .extend_role(
            "Typical Phrases",
            [
                "I’ve analyzed the latest market trends and have prepared a detailed report for your review.",
                "It’s important to align your investment goals with your long-term financial strategy.",
                "Let me walk you through this portfolio optimization model for better returns."
            ]
        )

        .set_role("Interaction Rules", "Maintain a professional and approachable tone. Avoid giving speculative or high-risk advice unless explicitly requested by the user.")
)





agent_Gabriel.append_status_mapping(

    "User Intent", "Casual Chat",

    "instruct",
    "When responding, follow the order below:\n" +
    "First, acknowledge and show understanding of the important information and possible emotions contained in the user's input.\n" +
    "Then, provide your response to the user's input.\n" +
    "Finally, suggest possible topics to explore next, which can either continue the current topic or start a new one.\n" +
    "Note: Use conversational expressions and avoid structured expressions like 'firstly... secondly... lastly'."
)

agent_Gabriel.append_status_mapping(

     "User Intent", "want to have have a research report about an investment bank",
    "output",

    {
        "answers": (
            [{
                "question_topic": ("str", "根据{input}判断关键问题"),
                "answer": ("str", "你对{question_topic}的直接回答"),
                "suggestion": ("str", "你对回答/解决{question_topic}的进一步行动建议，如果没有可以输出''"),
                "relative_questions": ([("str", "与{question_topic}相关的可以探讨的其他问题")], "不超过3个")
            }],
            "根据{input}对用户提问进行回答，用户有多个提问，应该在{answers}中拆分成多个{question_topic}以及对应的回答"
        )
    }
)


tool_info = {
    "tool_name": "write report",
    "desc": "input a name of a investment bank,output a research report for this investment bank, by using work flow",
    "args": {
        "user_id": (
            "int",
            "int auto_increment PRIMARY KEY, a user id in data base "
        ),
        "company_name": (
            "str",
            "a symbol for a investment bank",
        ),
        "number_of_news":(
            "int",
            " an int that the number that user want to generate the report"

        ),
        "agent":(
            "str",
            "the name of the agent that use to generate the report"
        )

    },
    "func": create_report
}

Agently.global_tool_manager.register(**tool_info)



create_report(1, "MS",20, agent_Gabriel)


