# Report Quality Assurance & Reliability

The following documents lists some of the ways through which we can gurantee the validness of the AI-generated analysis report.

### **1. Schema Validation**

The LLM can hallucinate metrics, misquote data, or invent facts not in the source JSON.

In python there's a module called Pydantic that provides several methods of validating a schema for expected report format


### **2. Source Data Attribution & Traceability**

If a recommendation says "keyword X has 500k monthly searches" but where did that come from? The LLM prompt must require: "For every metric you cite, include [SOURCE: filename / section]"


### **3. Hallucination Detection & Fact-Checking**

LLMs tend to invent metrics or trends that don't exist in the data.

- Extract all factual claims (numbers, competitor names, metrics) from LLM report
- Cross-reference against source data
- Flag novel metrics not in source as potential hallucinations - for human review.


### **4. Human Review Gate & Sign-Off**

Bad reports should not reach decision-makers without review.

- Generate review brief highlighting all concerns
- Require human sign-off before report goes to decision-makers
- Track who approved the report and when
- Include validation results in final report (transparency)
- Store sign-off metadata in audit log


