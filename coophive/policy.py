class Policy:
    def __init__(self, name, algorithm):
        self.name = name
        self.algorithm = algorithm  # This could be 'fit/predict', 'train/infer', 'train/evaluate', etc.

    def make_decision(self, match, local_info):
        """
        Make a decision based on the current state and the chosen algorithm.
        
        Args:
            match: The current Match object being considered
            local_info: Local information available to the agent
            
        Returns:
            str: 'accept', 'reject', or 'negotiate'
        """
        message_history = match.get_message_history()
        
        if self.algorithm == 'fit/predict':
            return self._fit_predict_decision(match, local_info, message_history)
        elif self.algorithm == 'train/infer':
            return self._train_infer_decision(match, local_info, message_history)
        elif self.algorithm == 'train/evaluate':
            return self._train_evaluate_decision(match, local_info, message_history)
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")

    def _fit_predict_decision(self, match, local_info, message_history):
        # Implement fit/predict decision logic. should return "accept", "reject", or "negotiate"
        pass

    def _train_infer_decision(self, match, local_info, message_history):
        # Implement train/infer decision logic. should return "accept", "reject", or "negotiate"
        pass

    def _train_evaluate_decision(self, match, local_info, message_history):
        # Implement train/evaluate decision logic. should return "accept", "reject", or "negotiate".
        pass