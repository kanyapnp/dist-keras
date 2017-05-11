"""Evaluation module.

An evaluator will evaluate a dataframe according to specific requirements.
"""

from pyspark.sql.functions import udf
from pyspark.mllib.linalg import DenseVector, DoubleType

class Evaluator(object):
    """An evaluator is an abstract class which will, given a label and a prediction,
       will compute an evaluation metric.

    # Arguments
        label_col: string. Column name of the label.
        prediction_col: string. Column name of the prediction.
    """

    def __init__(self, label_col="label", prediction_col="prediction"):
        self.label_column = label_col
        self.prediction_column = prediction_col

    def evaluate(self, dataframe):
        """Evalutes the specified dataframe.

        # Arguments
            dataframe: dataframe. Spark Dataframe.
        """
        raise NotImplementedError


class AccuracyEvaluator(Evaluator):
    """Computes the accuracy of the prediction based on the label.

    # Arguments
        label_col: string. Label column.
        prediction_col: string. Prediction column.
    """

    def __init__(self, label_col="label", prediction_col="prediction"):
        # Initialize the parent structure.
        super(AccuracyEvaluator, self).__init__(label_col, prediction_col)

    def evaluate(self, dataframe):
        # Count the total number of instances.
        num_instances = dataframe.count()
        # Extract the matching indexes.
        cleaned = dataframe.where(dataframe[self.prediction_column] == dataframe[self.label_column])
        # Fetch the number of correctly guessed instances.
        validated_instances = cleaned.count()

        return float(validated_instances) / float(num_instances)

    
class MseEvaluator(Evaluator):
    """Computes the MSE accuracy of the prediction based on the label.
       It adds a new column on the dataframe, default: mse_score

    # Arguments
        label_col: string. Label column.
        prediction_col: string. Prediction column.
        score_col: string. MSE score column
    """

    def __init__(self, label_col="label", prediction_col="prediction", score_col="mse_score"):
        # Initialize the parent structure.
        super(AccuracyEvaluator, self).__init__(label_col, prediction_col)
        self.score_col = score_col

    def evaluate(self, dataframe):
        # spark mse udf function 
        def mse_func(x,y):
            return float((DenseVector(x-y).values**2).mean())
        
        mse = udf(mse_func, DoubleType())        
        # apply to each predicted row
        dataframe = dataframe.withColumn(self.score_col, mse(dataframe[self.label_column],dataframe[self.prediction_column]))         
        # average over all score results.
        mse_score = dataframe.select(self.score_col).groupBy().avg(self.score_col).collect()[0][0]

        #cast to float and return
        return float(mse_score)
