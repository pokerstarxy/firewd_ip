"""empty message

Revision ID: 8c529ca88e77
Revises: 04d7dab273f4
Create Date: 2018-06-25 16:15:01.775907

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8c529ca88e77'
down_revision = '04d7dab273f4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('ip_info', 'lastest_aa_bb')
    op.add_column('ip_ipseg_info', sa.Column('lastest_aa_bb', sa.Integer(), nullable=True))
    op.drop_column('ip_ipseg_info', 'dd')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ip_ipseg_info', sa.Column('dd', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.drop_column('ip_ipseg_info', 'lastest_aa_bb')
    op.add_column('ip_info', sa.Column('lastest_aa_bb', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    # ### end Alembic commands ###