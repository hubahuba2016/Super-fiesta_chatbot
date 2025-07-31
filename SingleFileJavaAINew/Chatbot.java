import java.io.*;
import java.sql.*;
import java.util.*;
import java.util.stream.*;
import org.apache.commons.math3.linear.*;

public class Chatbot {
    private static final String DB_NAME = "chatbot.db";

  public static void main(String[] args) throws Exception {
        try (Connection conn = connectDB()) {
            importTrainingData(conn, "chatbot_training_data.txt");
            Scanner scanner = new Scanner(System.in);
            System.out.println("📱 Simple Chatbot (Java + SQLite)");
            System.out.println("Type 'train' to teach, 'exit' to quit.\n");

            while (true) {
                System.out.print("You: ");
                String input = scanner.nextLine().trim().toLowerCase();
                if (input.equals("exit")) break;
                else if (input.equals("train")) {
                    trainBot(conn, scanner);
                } else {
                    System.out.println("Bot: " + getResponse(conn, input));
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

        private static Connection connectDB() throws SQLException, ClassNotFoundException {
    Class.forName("org.sqlite.JDBC"); // <-- ADD THIS LINE
    Connection conn = DriverManager.getConnection("jdbc:sqlite:" + DB_NAME);
    try (Statement stmt = conn.createStatement()) {
        stmt.executeUpdate(
            "CREATE TABLE IF NOT EXISTS chatbot (\n" +
            "    question TEXT PRIMARY KEY,\n" +
            "    answer TEXT NOT NULL\n" +
            ")"
        );
    }
    return conn;
}

    private static void importTrainingData(Connection conn, String filename) throws IOException, SQLException {
        File file = new File(filename);
      if (!file.exists()) {
    System.out.println("Training file '" + filename + "' not found in: " + file.getAbsolutePath());
    return;
        }

        BufferedReader reader = new BufferedReader(new FileReader(file));
        String line;
        String question = null, answer = null;
        PreparedStatement ps = conn.prepareStatement("INSERT OR REPLACE INTO chatbot (question, answer) VALUES (?, ?)");

        while ((line = reader.readLine()) != null) {
            line = line.trim();
            if (line.startsWith("Q: ")) question = line.substring(3).trim().toLowerCase();
            else if (line.startsWith("A: ")) {
                answer = line.substring(3).trim();
                if (question != null && answer != null) {
                    ps.setString(1, question);
                    ps.setString(2, answer);
                    ps.executeUpdate();
                    question = answer = null;
                }
            }
        }

        reader.close();
        System.out.println("Training data imported successfully.");
    }

    private static void trainBot(Connection conn, Scanner scanner) throws SQLException {
        System.out.println("Training mode. Add a new question-answer pair.");
        System.out.print("Question: ");
        String question = scanner.nextLine().trim().toLowerCase();
        System.out.print("Answer: ");
        String answer = scanner.nextLine().trim();

        if (!question.isEmpty() && !answer.isEmpty()) {
            PreparedStatement ps = conn.prepareStatement("INSERT OR REPLACE INTO chatbot (question, answer) VALUES (?, ?)");
            ps.setString(1, question);
            ps.setString(2, answer);
            ps.executeUpdate();
            System.out.println("Training saved.\n");
        } else {
            System.out.println("Empty input! Try again.\n");
        }
    }

    private static String getResponse(Connection conn, String input) throws SQLException {
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT question, answer FROM chatbot");

        List<String> questions = new ArrayList<>();
        List<String> answers = new ArrayList<>();
        while (rs.next()) {
            questions.add(rs.getString("question"));
            answers.add(rs.getString("answer"));
        }

        if (questions.isEmpty()) return "I'm not trained yet. Type 'train' to teach me.";

        List<String> allTexts = new ArrayList<>(questions);
        allTexts.add(input);

        Map<String, Integer> vocab = buildVocab(allTexts);
        RealVector inputVec = vectorize(input, vocab);
        double bestScore = 0.0;
        String bestAnswer = "I don't know how to respond to that. Try training me.";

        for (int i = 0; i < questions.size(); i++) {
            RealVector qVec = vectorize(questions.get(i), vocab);
            double sim = cosineSimilarity(inputVec, qVec);
            if (sim > bestScore) {
                bestScore = sim;
                bestAnswer = answers.get(i);
            }
        }

        return bestScore > 0.4 ? bestAnswer : "I don't know how to respond to that. Try training me.";
    }

    private static Map<String, Integer> buildVocab(List<String> texts) {
        Set<String> words = texts.stream()
                .flatMap(text -> Arrays.stream(text.split("\\s+")))
                .collect(Collectors.toSet());

        Map<String, Integer> vocab = new HashMap<>();
        int index = 0;
        for (String word : words) {
            vocab.put(word, index++);
        }

        return vocab;
    }

    private static RealVector vectorize(String text, Map<String, Integer> vocab) {
        double[] vec = new double[vocab.size()];
        for (String word : text.split("\\s+")) {
            if (vocab.containsKey(word)) {
                vec[vocab.get(word)] += 1.0;
            }
        }
        return new ArrayRealVector(vec);
    }

    private static double cosineSimilarity(RealVector v1, RealVector v2) {
        double dot = v1.dotProduct(v2);
        double norm1 = v1.getNorm();
        double norm2 = v2.getNorm();
        return (norm1 == 0 || norm2 == 0) ? 0.0 : dot / (norm1 * norm2);
    }
}
