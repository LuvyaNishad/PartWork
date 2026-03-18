import com.formdev.flatlaf.FlatDarculaLaf; // Upgraded to Dark Mode!
import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.Vector;

public class MainDashboard extends JFrame {

    private JPanel cardPanel; // The container that holds the changing screens
    private CardLayout cardLayout; // The manager that flips the screens

    private JTable jobTable;
    private DefaultTableModel tableModel;

    public MainDashboard() {
        setTitle("PartWork - Professional Workspace");
        setSize(1000, 700);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout());

        // ==========================================
        // 1. CREATE THE SIDEBAR (WEST)
        // ==========================================
        JPanel sidebar = new JPanel();
        sidebar.setLayout(new BoxLayout(sidebar, BoxLayout.Y_AXIS));
        sidebar.setPreferredSize(new Dimension(250, 0));
        sidebar.setBackground(new Color(43, 45, 48));
        sidebar.setBorder(BorderFactory.createEmptyBorder(20, 10, 20, 10));

        JLabel brandLabel = new JLabel("PartWork.");
        brandLabel.setFont(new Font("Segoe UI", Font.BOLD, 28));
        brandLabel.setForeground(new Color(88, 166, 255)); // Bright Blue
        brandLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        JButton btnFindWork = createNavButton("🔍 Find Work");
        JButton btnMyApps = createNavButton("📁 My Applications");
        JButton btnWallet = createNavButton("💳 Escrow Wallet");

        // Action Listeners for Navigation
        btnFindWork.addActionListener(e -> cardLayout.show(cardPanel, "FEED_VIEW"));
        // You can add panels for the other buttons later!

        sidebar.add(brandLabel);
        sidebar.add(Box.createRigidArea(new Dimension(0, 40))); // Spacing
        sidebar.add(btnFindWork);
        sidebar.add(Box.createRigidArea(new Dimension(0, 10)));
        sidebar.add(btnMyApps);
        sidebar.add(Box.createRigidArea(new Dimension(0, 10)));
        sidebar.add(btnWallet);

        // ==========================================
        // 2. CREATE THE MAIN CONTENT AREA (CENTER)
        // ==========================================
        cardLayout = new CardLayout();
        cardPanel = new JPanel(cardLayout);

        // Build Screen 1: The Job Feed
        JPanel jobFeedScreen = createJobFeedScreen();
        // Build Screen 2: The Details View (Empty for now, fills on click)
        JPanel jobDetailsScreen = createJobDetailsScreen();

        // Add screens to the card deck
        cardPanel.add(jobFeedScreen, "FEED_VIEW");
        cardPanel.add(jobDetailsScreen, "DETAILS_VIEW");

        // Assemble the Main Window
        add(sidebar, BorderLayout.WEST);
        add(cardPanel, BorderLayout.CENTER);
    }

    // Helper method to make sidebar buttons look nice
    private JButton createNavButton(String text) {
        JButton btn = new JButton(text);
        btn.setMaximumSize(new Dimension(200, 40));
        btn.setFont(new Font("Segoe UI", Font.BOLD, 14));
        btn.setFocusPainted(false);
        btn.setHorizontalAlignment(SwingConstants.LEFT);
        return btn;
    }

    // ==========================================
    // SCREEN 1: THE JOB FEED (Your table)
    // ==========================================
    private JPanel createJobFeedScreen() {
        JPanel panel = new JPanel(new BorderLayout(10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        JLabel title = new JLabel("Active Opportunities");
        title.setFont(new Font("Segoe UI", Font.BOLD, 22));
        panel.add(title, BorderLayout.NORTH);

        Vector<String> columns = new Vector<>();
        columns.add("OppID"); // Hidden Column
        columns.add("Role Title");
        columns.add("Company");
        columns.add("Type");
        columns.add("Location");

        tableModel = new DefaultTableModel(columns, 0) {
            @Override
            public boolean isCellEditable(int row, int column) { return false; } // Prevent typing in cells
        };
        jobTable = new JTable(tableModel);

        // Hide the OppID column from the user, but keep it in the data!
        jobTable.removeColumn(jobTable.getColumnModel().getColumn(0));

        jobTable.setRowHeight(35);
        jobTable.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        jobTable.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);

        // MAGIC: Listen for double-clicks on the table!
        jobTable.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                if (evt.getClickCount() == 2 && jobTable.getSelectedRow() != -1) {
                    // Grab data from the clicked row
                    int viewRow = jobTable.getSelectedRow();
                    int modelRow = jobTable.convertRowIndexToModel(viewRow);

                    String oppId = (String) tableModel.getValueAt(modelRow, 0); // The hidden ID!
                    String role = (String) tableModel.getValueAt(modelRow, 1);
                    String company = (String) tableModel.getValueAt(modelRow, 2);

                    // TODO: You would call JobDAO here to get the full description based on oppId
                    System.out.println("Opening details for OppID: " + oppId);

                    // Flip the card to the Details Screen
                    cardLayout.show(cardPanel, "DETAILS_VIEW");
                }
            }
        });

        JScrollPane scrollPane = new JScrollPane(jobTable);
        panel.add(scrollPane, BorderLayout.CENTER);

        loadData(); // Fill the table
        return panel;
    }

    // ==========================================
    // SCREEN 2: THE DETAILS VIEW
    // ==========================================
    private JPanel createJobDetailsScreen() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBorder(BorderFactory.createEmptyBorder(30, 40, 30, 40));

        JLabel title = new JLabel("Opportunity Details");
        title.setFont(new Font("Segoe UI", Font.BOLD, 26));

        JTextArea descriptionArea = new JTextArea("This is where the detailed description, required skills, and payout milestones will load when you click a job.\n\nImagine fetching the RequiredSkills and MilestoneLedger data here!");
        descriptionArea.setFont(new Font("Segoe UI", Font.PLAIN, 16));
        descriptionArea.setLineWrap(true);
        descriptionArea.setWrapStyleWord(true);
        descriptionArea.setEditable(false);
        descriptionArea.setOpaque(false);

        JButton backBtn = new JButton("⬅ Back to Feed");
        backBtn.setFont(new Font("Segoe UI", Font.BOLD, 14));
        backBtn.addActionListener(e -> cardLayout.show(cardPanel, "FEED_VIEW")); // Flips back!

        JPanel topPanel = new JPanel(new BorderLayout());
        topPanel.add(backBtn, BorderLayout.WEST);
        topPanel.add(title, BorderLayout.CENTER);

        panel.add(topPanel, BorderLayout.NORTH);
        panel.add(descriptionArea, BorderLayout.CENTER);

        // Add a giant "Apply Now" button at the bottom
        JButton applyBtn = new JButton("Submit Application");
        applyBtn.setBackground(new Color(46, 139, 87)); // Sea Green
        applyBtn.setForeground(Color.WHITE);
        applyBtn.setFont(new Font("Segoe UI", Font.BOLD, 16));
        applyBtn.setPreferredSize(new Dimension(0, 50));
        panel.add(applyBtn, BorderLayout.SOUTH);

        return panel;
    }

    private void loadData() {
        tableModel.setRowCount(0);
        Vector<Vector<String>> jobs = JobDAO.getActiveJobs();
        for (Vector<String> row : jobs) {
            tableModel.addRow(row);
        }
    }

    public static void main(String[] args) {
        // TURN ON DARK MODE
        try {
            UIManager.setLookAndFeel(new FlatDarculaLaf());
        } catch (Exception ex) {
            System.err.println("Failed to initialize UI theme.");
        }

        SwingUtilities.invokeLater(() -> new MainDashboard().setVisible(true));
    }
}