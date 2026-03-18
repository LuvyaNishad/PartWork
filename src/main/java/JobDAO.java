import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.Vector;

public class JobDAO {
    public static Vector<Vector<String>> getActiveJobs() {
        Vector<Vector<String>> data = new Vector<>();
        // Added o.OppID at the beginning of the SELECT
        String sql = "SELECT o.OppID, o.RoleTitle, e.BusinessName, o.Type, o.City " +
                "FROM Opportunity o " +
                "JOIN Posts p ON o.OppID = p.OppID " +
                "JOIN Employer e ON p.EmployerID = e.EmployerID " +
                "WHERE o.Status = 'Active'";

        try (Connection conn = DBConnection.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {

            while (rs.next()) {
                Vector<String> row = new Vector<>();
                row.add(rs.getString("OppID")); // Hidden ID
                row.add(rs.getString("RoleTitle"));
                row.add(rs.getString("BusinessName"));
                row.add(rs.getString("Type"));
                row.add(rs.getString("City"));
                data.add(row);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return data;
    }
}