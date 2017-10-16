package org.sample.test;

import java.sql.Connection; 
import java.sql.DriverManager; 
import java.sql.PreparedStatement; 
import java.sql.ResultSet; 
import java.sql.SQLException; 
import java.sql.Statement; 
import java.util.ArrayList;
import java.util.Arrays;

import javax.servlet.http.HttpServletRequest;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

@Path("/")
public class testJDBC {
	
	public Connection ConnectDB() throws ClassNotFoundException, SQLException {
		Class.forName("com.mysql.jdbc.Driver");
		Connection conn = null;
		conn = DriverManager.getConnection("jdbc:mysql://140.118.70.162:13306/jobguide?useUnicode=true&characterEncoding=UTF8","jobguide","zNW3hw1HjMsQvOc9");
		//conn = DriverManager.getConnection("jdbc:mysql://140.118.70.162:13306/jobguide","jobguide", "zNW3hw1HjMsQvOc9");
		
		return conn;
	}
	
	//就業潮，該年各月的徵職文章量
	public ResultSet GetJobsAmount(int year, Connection conn) throws SQLException {
		Statement st = conn.createStatement();
		String sql = "SELECT month, total FROM ptt_spark_job WHERE year = " + year;
		ResultSet rs = st.executeQuery(sql);
		return rs;
	}
	
	//平均薪資
	public ResultSet GetSalaryAverage(int year, Connection conn) throws SQLException {
		Statement st = conn.createStatement();
		String sql = "SELECT work_area, salary FROM ptt_spark_average WHERE year = " + year;
		ResultSet rs = st.executeQuery(sql);
		return rs;
	}
	
	//UTF-8 BOM
	public String RemoveUTF8BOM(String tmp) {
		if (tmp.startsWith("\ufeff")) {
	        tmp = tmp.substring(1);
		}
		return tmp;
	}
	
	//搜尋公司
	public ResultSet SearchCorporationList(String corporation, Connection conn) throws SQLException {
		Statement st = conn.createStatement();
		String sql = "SELECT * FROM ptt_corporation_rank WHERE corporation LIKE '%" + corporation + "%'";
		ResultSet rs = st.executeQuery(sql);
		return rs;
	}
	
	//公司評價
	public ResultSet GetCorporationRanking(String name, Connection conn) throws SQLException {
		Statement st = conn.createStatement();
		String sql = "SELECT * FROM ptt_corporation_rank WHERE corporation = '" + name + "'";
		ResultSet rs = st.executeQuery(sql);
		return rs;
	}
	
	//公司職缺
	public ResultSet GetJobs(String name, Connection conn) throws SQLException {
		Statement st = conn.createStatement();
		String sql = "SELECT work, article_id FROM ptt_content_analyze WHERE corporation LIKE '%" + name + "%'";
		ResultSet rs = st.executeQuery(sql);
		return rs;
	}
	
	//分析各類群平均薪資
	public void AnalyzeSalary(ResultSet rs, String[] tmpList, int[] tmp) throws SQLException {
		while(rs.next()) {
			for (int i = 0; i < 19; i++) {
				if(RemoveUTF8BOM(rs.getString("work_area")).equals(tmpList[i])) {
					tmp[i] = rs.getInt("salary");
					}
			}
		}
	}
	
	//各職缺細部介紹
	public ResultSet GetWorkDetail(String id, Connection conn) throws SQLException {
		Statement st = conn.createStatement();
		String sql = "SELECT * FROM ptt_content_analyze WHERE article_id = '" + id + "'";
		ResultSet rs = st.executeQuery(sql);
		return rs;
	}
	
	//回傳格式
	public Response responseJSONString(String output) {
		return Response.ok("").header("Access-Control-Allow-Origin", "*")
				.entity(output)
				.build();
	}
	
	@POST
	@Path("/employment")
	@Produces(MediaType.APPLICATION_JSON)
	public Response GetEmploymentTrend(String request) throws ClassNotFoundException, SQLException, JSONException {
		Connection conn = ConnectDB();
		JSONArray array = new JSONArray();
		int tmpSix[] = new int[12];
		int tmpSeven[] = new int[12];
		Arrays.fill(tmpSix, 0);
		Arrays.fill(tmpSeven, 0);
		ResultSet rs = GetJobsAmount(2016, conn);
		ResultSet tmpRs = GetJobsAmount(2017, conn);
		while(rs.next()) {
			int tempMonth = rs.getInt("month");
			tmpSix[tempMonth-1] = rs.getInt("total");
		}
		while(tmpRs.next()) {
			int tempMonth = tmpRs.getInt("month");
			tmpSeven[tempMonth-1] = tmpRs.getInt("total");
		}
		for(int i = 0; i < 12; i++) {
			JSONObject tmp = new JSONObject();
			tmp.put("month", Integer.toString(i + 1) + "月");
			tmp.put("2016", tmpSix[i]);
			tmp.put("2017", tmpSeven[i]);
			array.put(tmp);
		}
		JSONObject response = new JSONObject();
		response.put("array", array);
		return responseJSONString(response.toString());
	}
	
	@POST
	@Path("/searchCorporation")
	@Produces(MediaType.APPLICATION_JSON)
	public Response SearchCorporation(String request) throws ClassNotFoundException, SQLException, JSONException {
		Connection conn = ConnectDB();
		JSONObject tmpJson = new JSONObject(request);
		JSONArray array = new JSONArray();
		JSONObject response = new JSONObject();
		String corporation = tmpJson.getString("name");
		ResultSet rs = SearchCorporationList(corporation, conn);
		if(!rs.next()) {
			response.put("search", "fail");
		}
		else {
			rs.beforeFirst();
			while(rs.next()) {
				array.put(rs.getString("corporation"));
				System.out.println(rs.getString("corporation"));
			}
			response.put("search", "success");
			response.put("array", array);
		}
		return responseJSONString(response.toString());
	}
	
	@POST
	@Path("/corporationDetails")
	@Produces(MediaType.APPLICATION_JSON)
	public Response GetCorporationDetails(String request) throws ClassNotFoundException, SQLException, JSONException {
		Connection conn = ConnectDB();
		JSONObject tmpJson = new JSONObject(request);
		JSONObject response = new JSONObject();
		JSONArray array = new JSONArray();
		String name = tmpJson.getString("name");
		ResultSet rs = GetCorporationRanking(name, conn);
		while(rs.next()) {
			response.put("name", name);
			response.put("rank", rs.getFloat("rank") * 1000);
		}
		rs = GetJobs(name, conn);
		System.out.println(name);
		while(rs.next()) {
			System.out.println(rs.getString("work"));
			JSONObject tmp = new JSONObject();
			tmp.put("work", rs.getString("work"));
			tmp.put("id", rs.getString("article_id"));
			array.put(tmp);
		}
		response.put("jobs", array);
		return responseJSONString(response.toString());
	}
	
	@POST
	@Path("/getAverage")
	@Produces(MediaType.APPLICATION_JSON)
	public Response GetAverageSalary() throws ClassNotFoundException, SQLException, JSONException {
		Connection conn = ConnectDB();
		String tmpList[] = {"資訊學群", "工程學群", "數理化學群", "醫藥衛生學群", "生命科學學群", "生物資源學群", "地球與環境學群", "建築與設計學群", "藝術學群", "社會與心理學群", "大眾傳播學群", "外語學群", "文史哲學群", "教育學群", "法政學群", "管理學群", "財經學群", "遊憩與運動學群", "其他"};
		String list[] = {"資訊學群", "工程學群", "數理化學", "醫藥衛生", "生命科學", "生物資源", "地球環境", "建築設計", "藝術學群", "社會與心理", "大眾傳播", "外語學群", "文史哲學群", "教育學群", "法政學群", "管理學群", "財經學群", "遊憩運動", "其他"};
		int tmpSix[] = new int[19];
		int tmpSeven[] = new int[19];
		JSONObject response = new JSONObject();
		ResultSet rs = GetSalaryAverage(2016, conn);
		AnalyzeSalary(rs, tmpList, tmpSix);
		rs = GetSalaryAverage(2017, conn);
		AnalyzeSalary(rs, tmpList, tmpSeven);
		JSONArray array = new JSONArray();
		for(int i = 0; i < 19; i++) {
			JSONObject tmp = new JSONObject();
			tmp.put("category", list[i]);
			tmp.put("2016", tmpSix[i]);
			tmp.put("2017", tmpSeven[i]);
			array.put(tmp);
		}
		response.put("array", array);
		return responseJSONString(response.toString());
	}
	
	@POST
	@Path("getDetailsOfWork")
	@Produces(MediaType.APPLICATION_JSON)
	public Response GetDetailsOfWork(String request) throws ClassNotFoundException, SQLException, JSONException {
		Connection conn = ConnectDB();
		JSONObject tmpJson = new JSONObject(request);
		String id = tmpJson.getString("id");
		ResultSet rs = GetWorkDetail(id, conn);
		JSONObject response = new JSONObject();
		while(rs.next()) {
			response.put("work", rs.getString("work"));
			response.put("corporation", rs.getString("corporation"));
			response.put("workcontent", rs.getString("work_content"));
			response.put("location", rs.getString("work_location"));
			response.put("salary", rs.getInt("salary"));
			response.put("contact", rs.getString("contact"));
		}
		return responseJSONString(response.toString());
		
	}
}
