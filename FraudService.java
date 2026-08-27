public class FraudService {

    public String checkFraud(double amount) {

        if (amount > 10000) {
            return "FRAUD";
        } 
        else if (amount > 5000) {
            return "SUSPICIOUS";
        } 
        else {
            return "NORMAL";
        }
    }
}