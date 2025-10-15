import numpy as np
from datetime import datetime, date
from typing import Union, Optional
import random
import time


class QAgent():
    def __init__(
            self, 
            table_shape: tuple = (25+1, 20+1, 12),
            epsilon: float = 0.999, 
            epsilon_min: float = 0.01, 
            epsilon_decay: float = 0.999, 
            gamma: float = 0.95, 
            lr: float = 0.8
        ):
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.gamma = gamma
        self.lr = lr
        self.Q = np.zeros(table_shape, dtype = np.uint32)
        self.A = [x for x in range(0,12,1)] # [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]

    def train(self, 
        obs_1: int, obs_2: int, 
        a: int, 
        r: float, 
        obs_next_1: int, obs_next_2: int
    ):
        self.Q[obs_1,obs_2,a] = self.Q[obs_1,obs_2,a] + \
            self.lr * (r + self.gamma*np.max(self.Q[obs_next_1,obs_next_2,a]) - self.Q[obs_1,obs_2,a])

    def act(self, obs_1: int, obs_2: int) -> int:
        if random.uniform(0, 1) > self.epsilon:
            a = np.argmax(self.Q[obs_1,obs_2,:])
        else:
            a = random.choice(self.A)
        return a
    
    def remember_(self, experience: list):
        self.sequence.append(experience)

    def reset_memory(self):
        self.sequence = []


class MPS():

    def __init__(
        self,
        forecast_sales: np.ndarray,         # Planning data of length period_info[1]+[2]
        num_working_days: np.ndarray,       # Planning data of length period_info[1]+[2]
        actual_sales: np.ndarray,           # Historical data of length period_info[0] depicting past sales
        actual_products: np.ndarray,        # Historical data of length period_info[0] depicting actual number of units produced
        num_workers: np.ndarray,            # Historical data of length period_info[0] depicting past number of workers
        planned_products: np.ndarray,       # Historical data of length period_info[0] depicting planned number of units produced
        planned_ending_inv: np.ndarray,     # Historical data of length period_info[0] depicting planned ending inventory
        actual_ending_inv: np.ndarray,      # Historical data of length period_info[0] depicting actual ending inventory
        actual_dos: np.ndarray,             # Historical data of length period_info[0] depicting past days of supply
        period_info: np.ndarray,            # Of length 3, depicting the number of periods of [historical, plan, future]
        converter: np.ndarray,              # Convert rate between monetary and measurement unit
        labor_costs: np.ndarray,            # [hiring_cost, layoff_cost]
        id: str,                            # ID of product group
        planning_factor: int,               # Average value per unit, calculated from accounting records
        worker_productivity: int,           # Number of units per day per worker
        holding_cost: float,                # Carrying cost per item per period
        min_dos: float,                     # Minimum Day-of-supply
        agent: QAgent
    ):
        self.id = id
        self.planning_factor = planning_factor
        self.worker_productivity = worker_productivity
        self.holding_cost = holding_cost
        self.min_dos = min_dos
        self.converter = converter
        self.labor_costs = labor_costs
        self.actual_sales = actual_sales
        self.num_workers = num_workers
        self.actual_products = actual_products
        self.planned_products = planned_products
        self.planned_ending_inv = planned_ending_inv
        self.actual_ending_inv = actual_ending_inv
        self.actual_dos = actual_dos
        self.period_info = period_info
        self.forecast_sales = forecast_sales
        self.num_working_days = num_working_days
        self.agent = agent

        """
        Pre-compute
        """
        self.forecast_units = self.forecast_sales * 1e3 / self.planning_factor
        self.beginning_inv = self.actual_ending_inv[-1]
        self.beginning_workers = self.num_workers[-1]

        """
        For Mix
        """
        self.best_cost = -float("inf")
        self.best_sequence = []


    def chase(self, dos: Optional[np.ndarray] = None) -> dict:

        beg_inv = self.beginning_inv
        beg_work = self.beginning_workers
        hires = []
        layoffs = []

        if dos.__class__ == np.ndarray:

            for i in range(self.period_info[1]):

                idx_ = i+self.period_info[0]
                inv_i = dos[i] * self.forecast_units[idx_+1] / self.num_working_days[idx_+1]
                plan_prod_i = self.forecast_units[idx_] - beg_inv + inv_i
                self.planned_ending_inv = np.append(self.planned_ending_inv, inv_i)
                self.planned_products = np.append(self.planned_products, plan_prod_i)
                
                num_work_i = plan_prod_i * 1e3 / (self.worker_productivity * self.num_working_days[idx_+1])
                self.num_workers = np.append(self.num_workers, num_work_i)

                work_diff = num_work_i - beg_work
                if work_diff > 0:
                    hires.append(work_diff)
                    layoffs.append(0.0)
                elif work_diff < 0:
                    hires.append(0.0)
                    layoffs.append(-work_diff)
                else:
                    hires.append(0.0)
                    layoffs.append(0.0)

                beg_inv = inv_i
                beg_work = num_work_i
        
        elif dos == None:

            self.planned_products = self.forecast_units[:-self.period_info[-1]]
            self.num_workers = np.append(
                self.num_workers,
                self.forecast_units[self.period_info[0]:] * 1e3 / \
                    (np.array(self.num_working_days[self.period_info[0]:]) * self.worker_productivity)
            )[:-self.period_info[-1]]

            for i in range(self.period_info[1]):
                
                idx_ = i + self.period_info[0]
                inv_i = beg_inv + self.planned_products[idx_] - self.forecast_units[idx_]
                self.planned_ending_inv = np.append(self.planned_ending_inv, inv_i)

                work_diff = self.num_workers[idx_] - beg_work
                if work_diff > 0:
                    hires.append(work_diff)
                    layoffs.append(0.0)
                elif work_diff < 0:
                    hires.append(0.0)
                    layoffs.append(-work_diff)
                else:
                    hires.append(0.0)
                    layoffs.append(0.0)

                beg_inv = inv_i
                beg_work = self.num_workers[idx_]

            dos = np.array([np.nan] * self.period_info[1])

        del beg_inv
        del beg_work

        padding_ = [np.nan] * self.period_info[0]

        return {
            'Production': np.round(self.planned_products),
            'Inventory': np.round(self.planned_ending_inv),
            'DOS': np.append(self.actual_dos, dos),
            'Workers': np.round(self.num_workers),
            'Hiring': np.round(padding_ + hires),
            'Layoff': np.round(padding_ + layoffs)
        }


    def level(self):

        cumForecast = np.sum(self.forecast_units[self.period_info[0]:-self.period_info[2]])
        required_ending_inv = self.forecast_units[-1] * self.min_dos / self.num_working_days[-1]
        total_working_days = np.sum(self.num_working_days[self.period_info[0]:-self.period_info[2]])
        total_required_inv = cumForecast - self.beginning_inv + required_ending_inv
        workers_per_period = total_required_inv * 1e3 / (self.worker_productivity * total_working_days)

        self.num_workers = np.append(self.num_workers, [workers_per_period] * self.period_info[1])
        self.planned_products = np.append(
            self.planned_products,
            workers_per_period * self.worker_productivity * self.num_working_days[self.period_info[0]:-self.period_info[2]] / 1e3
        )
        print(np.round(self.planned_products))

        work_diff = workers_per_period - self.beginning_workers
        hires = [np.nan] * self.period_info[0]
        layoffs = [np.nan] * self.period_info[0]
        if work_diff > 0:
            hires = hires + [work_diff] + [0.0] * (self.period_info[1] - 1)
            layoffs = layoffs + [0.0] * self.period_info[1]
        elif work_diff < 0:
            hires = hires + [work_diff] + [0.0] * self.period_info[1]
            layoffs = layoffs + [-work_diff] + [0.0] * (self.period_info[1] - 1)
        else:
            hires = hires + [0.0] * self.period_info[1]
            layoffs = layoffs + [0.0] * self.period_info[1]

        beg_inv = self.beginning_inv

        for i in range(self.period_info[1]):

            idx_ = i+self.period_info[0]
            inv_i = beg_inv + self.planned_products[idx_] - self.forecast_units[idx_]
            dos_i = inv_i * self.num_working_days[idx_+1] / self.forecast_units[idx_+1]
            self.planned_ending_inv = np.append(self.planned_ending_inv, inv_i)
            self.actual_dos = np.append(self.actual_dos, dos_i)

            beg_inv = inv_i

        del beg_inv

        return {
            'Production': np.round(self.planned_products),
            'Inventory': np.round(self.planned_ending_inv),
            'DOS': np.round(self.actual_dos, 1),
            'Workers': np.round(self.num_workers),
            'Hiring': np.round(hires),
            'Layoff': np.round(layoffs)
        }


    def specify(self, chosen_num_workers: list) -> dict:

        beg_inv = self.beginning_inv
        beg_work = self.beginning_workers
        hires = []
        layoffs = []

        for i in range(self.period_info[1]):

            idx_ = i+self.period_info[0]
            work_diff = chosen_num_workers[i]
            num_work_i = beg_work + work_diff
            self.num_workers = np.append(self.num_workers, num_work_i)

            if work_diff > 0:
                hires.append(work_diff)
                layoffs.append(0.0)
            elif work_diff < 0:
                hires.append(0.0)
                layoffs.append(-work_diff)
            else:
                hires.append(0.0)
                layoffs.append(0.0)

            plan_prod_i = num_work_i * self.worker_productivity * self.num_working_days[idx_] * 1e-3
            self.planned_products = np.append(self.planned_products, plan_prod_i)

            inv_i = beg_inv + plan_prod_i - self.forecast_units[idx_]
            self.planned_ending_inv = np.append(self.planned_ending_inv, inv_i)

            dos_i = inv_i * self.num_working_days[idx_+1] / self.forecast_units[idx_+1]
            self.actual_dos = np.append(self.actual_dos, dos_i)

            beg_inv = inv_i
            beg_work = num_work_i

        del beg_inv
        del beg_work

        padding_ = [np.nan] * self.period_info[0]

        return {
            'Production': np.round(self.planned_products),
            'Inventory': np.round(self.planned_ending_inv),
            'DOS': np.round(self.actual_dos),
            'Workers': np.round(self.num_workers),
            'Hiring': np.round(padding_ + hires),
            'Layoff': np.round(padding_ + layoffs)
        }


    def step(
        self, 
        work_diff: int, 
        current_inv: int, 
        current_work: int,
        idx_: int,
    ) -> list:
        work_diff = (work_diff - 5)*100
        labor_incur_cost = (work_diff > 0) * self.labor_costs[0] * work_diff + (work_diff < 0) * self.labor_costs[1] * (-work_diff)
        next_work = current_work + work_diff

        next_prod = next_work * self.worker_productivity * self.num_working_days[idx_] * 1e-3
        next_inv = current_inv + next_prod - self.forecast_units[idx_]
        inv_holding_cost = next_inv * self.holding_cost

        reward = labor_incur_cost + inv_holding_cost

        done = idx_ == 14

        # print(next_inv, current_inv, next_prod, self.forecast_units[idx_])
        current_inv_ = int(str(round(current_inv))[:-1]) - 5
        current_work_ = int(str(round(current_work))[:-2]) - 10

        next_inv_ = str(round(next_inv))[:-1]
        if (len(next_inv_) == 0) | (next_inv_ == '-'):
            next_inv_ = -1
        elif len(next_inv_) > 0:
            next_inv_ = int(next_inv_)
        next_work_ = int(str(round(next_work))[:-2]) - 10

        cond1 = next_inv_ < 0
        cond2 = next_inv_ > 25
        cond3 = next_work_ < 0
        cond4 = next_work_ > 20
        if cond1 | cond2 | cond3 | cond4:
            reward += 1e7
            terminated = True
        else:
            terminated = False
        if cond1 | cond2:
            next_inv_ = 25
        if cond3 | cond4:
            next_work_ = 20
        
        return current_inv, current_work, current_inv_, current_work_, reward, \
            next_inv, next_work, next_inv_, next_work_, done, terminated


    def run_ep(self) -> int:
        
        ep_R = 0
        self.reset()
        self.agent.reset_memory()
        obs_1, obs_2 = self.beginning_inv, self.beginning_workers

        for i in range(self.period_info[1]):

            idx_ = i + self.period_info[0]
            a = self.agent.act(obs_1, obs_2)
            obs_1, obs_2, obs_1_, obs_2_, r, obs_1_n, obs_2_n, obs_1_n_, obs_2_n_, done, terminated = self.step(
                work_diff = a,
                current_inv = obs_1,
                current_work = obs_2,
                idx_ = idx_
            )
            r = -1 * r
            self.agent.train(
                obs_1 = obs_1_, obs_2 = obs_2_,
                a = a, r = r,
                obs_next_1 = obs_1_n_,
                obs_next_2 = obs_2_n_
            )

            if self.agent.epsilon > self.agent.epsilon_min:
                self.agent.epsilon = self.agent.epsilon**i
            
            ep_R += r
            self.agent.remember_(
                experience = [obs_1, obs_2, obs_1_, obs_2_, (a - 5)*100, r, obs_1_n, obs_2_n, obs_1_n_, obs_2_n_, done, terminated]
            )
            obs_1 = obs_1_n
            obs_2 = obs_2_n

            if done | terminated:
                break
        
        return ep_R


    def mix(self, num_episodes: int = 55_000):

        cost_record = []

        for ep in range(1, num_episodes+1, 1):

            start = time.time()
            ep_R = self.run_ep()
            end = time.time()

            cost_record.append(ep_R)
            print(f"Episode {ep} | ${round(-ep_R):,} | {round(end - start, 6)} s")
            
            if ep_R > self.best_cost:
                self.best_sequence = self.agent.sequence
                self.best_cost = ep_R
        
        return cost_record, self.agent
    

    def reset(self):
        self.planned_products = self.planned_products[:self.period_info[0]]
        self.planned_ending_inv = self.planned_ending_inv[:self.period_info[0]]
        self.num_workers = self.num_workers[:self.period_info[0]]
        self.actual_dos = self.actual_dos[:self.period_info[0]]
        


if __name__ == '__main__':
    import polars as pl
    np.set_printoptions(threshold = np.inf, linewidth = np.inf)

    agent = QAgent(table_shape = (26, 21, 12))
    prod_group = MPS(
        forecast_sales = np.array([
            10.0, 13.1, 6.9,
            7.6, 8.4, 10.2, 9.0, 11.8, 7.0,
            8.6, 12.6, 14.4, 12.8, 15.8, 11.8,
            8.0
        ]),
        num_working_days = np.array([
            22, 20, 20,
            20, 21, 23, 20, 22, 22,
            10, 23, 20, 22, 20, 20,
            20
        ]),
        actual_sales = np.array([300, 400, 200]),
        actual_products = np.array([360, 455, 300]),
        num_workers = np.array([1892, 2731, 1437]),
        planned_products = np.array([333, 437, 230]),
        planned_ending_inv = np.array([100, 100, 100]),
        actual_ending_inv = np.array([60, 115, 215]),
        actual_dos = np.array([3.0, 11.5, 17.0]),
        period_info = np.array([3, 12, 1]),
        converter = [1e6, 1e3],
        labor_costs = np.array([200, 500]),
        id = 'A',
        planning_factor = 30,
        worker_productivity = 8,
        holding_cost = .02,
        min_dos = 5.0,
        agent = agent
    )


    """
    TEST LEVEL AND CHASE STRATEGY
    """
    # result = prod_group.chase(dos = np.array([5.0] * 12))
    # # result = prod_group.chase()
    # # result = prod_group.level()
    # result['Period'] = [-1 * i for i in reversed(range(1, prod_group.period_info[0]+1, 1))] \
    #     + [j for j in range(1, prod_group.period_info[1]+1, 1)]
    
    # df = pl.DataFrame(data = result)
    # df = df.select(['Period']+df.columns[:-1])
    # with pl.Config() as cfg:
    #     cfg.set_tbl_cols(-1)
    #     cfg.set_tbl_rows(-1)
    #     print(df)


    """
    TEST MIX STRATEGY
    """
    # N = 550_000
    # START = time.time()
    # # record, me = env.mix(num_episodes = N)
    # me = env.mix(num_episodes = N)
    # END = time.time()

    # print(f"Minimum cost: ${round(-env.best_cost):,}")
    # print(f"Total time taken: {round(END - START, 6)} seconds")
    # print(f"Per round taken: {round((END - START)/N, 6)} s")

    # print(f"Best sequence: ")
    # best_sequence = np.round(np.array(env.best_sequence))
    # best_sequence = best_sequence[:,[0, 1, 4, 5, 6, 7, 10, 11]]

    # df = pl.DataFrame(
    #     data = best_sequence,
    #     schema = {
    #         "Inv": pl.Int64, "Worker": pl.Int64,
    #         "Work_Diff": pl.Int64, "Cost": pl.Float64,
    #         "Inv_next": pl.Int64, "Worker_next": pl.Int64,
    #         "Done": pl.Boolean, "Terminated": pl.Boolean
    #     }
    # )
    # df.columns = ['Inv', 'Worker', 'Work_Diff', 'Cost', 'Inv_next', 'Worker_next', 'Done', 'Terminated']
    # df = df.with_columns(
    #     pl.Series('Period', [i for i in range(1, 13, 1)]),
    #     Cost = pl.col('Cost') * -1
    # ).select(
    #     ['Period', 'Inv', 'Worker', 'Work_Diff', 'Cost', 'Inv_next', 'Worker_next', 'Done', 'Terminated']
    # )
    # with pl.Config() as cfg:
    #     cfg.set_tbl_cols(-1)
    #     cfg.set_tbl_rows(-1)
    #     print(df)


    """
    TEST SPECIFY NUM WORKER STRATEGY
    """
    result = prod_group.specify(
        chosen_num_workers = [-300, 300, 0, 500, 200, 0, 400, 0, 0, 100, 200, 0]
        # [0, 0, 0, 554, 0, 0, 607, 138, 0, 0, 0, -475] -> Opt Book -> $1,391,900
        # [200, 0, 0, 100, 0, 200, 100, 500, 200, 0, 200, -100] # -> $1,267,619
        # [-300, 300, 0, 500, 200, 0, 400, 0, 0, 100, 200, 0] # -> $1,063,939
        # [100, 0, 100, -100, 400, 200, 100, 200, 0, 400, 100, -100] # -> $1_174_419
        # [100, 0, -200, 400, 200, 0, 600, 100, -100, 300, 100, 0] -> $1_203_000
        # [-400, 600, 100, 100, 100, 200, -100, 300, 400, 0, 100, 0] -> $1_241_400
        # [0, 0, 300, 100, 100, -100, 600, 200, 0, 100, 300, 0]
    )
    result['Period'] = [-1 * i for i in reversed(range(1, prod_group.period_info[0]+1, 1))] \
        + [j for j in range(1, prod_group.period_info[1]+1, 1)]
    
    df = pl.DataFrame(data = result)
    df = df.select(['Period']+df.columns[:-1]).filter(pl.col('Period') > 0)
    df = df.with_columns(
        Hiring_Cost = (pl.col('Hiring').fill_nan(0.0) * prod_group.labor_costs[0]).cast(pl.Int64),
        Layoff_Cost = (pl.col('Layoff').fill_nan(0.0) * prod_group.labor_costs[1]).cast(pl.Int64),
        Holding_Cost = (pl.col('Inventory').fill_nan(0.0) * prod_group.planning_factor * 1e3 * prod_group.holding_cost).cast(pl.Int64),
    ).with_columns(
        pl.sum_horizontal('Hiring_Cost', 'Layoff_Cost', 'Holding_Cost').alias('Per_Period_Cost')
    ).with_columns(
        pl.cum_sum('Per_Period_Cost').alias('Total')
    )
    with pl.Config() as cfg:
        cfg.set_tbl_cols(-1)
        cfg.set_tbl_rows(-1)
        print(df)
    




