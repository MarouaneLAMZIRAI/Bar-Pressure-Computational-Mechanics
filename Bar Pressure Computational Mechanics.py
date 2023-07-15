import vtk
from vtk.util import numpy_support
import numpy as np
from PyQt5 import QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setup_vtk()

    def setup_vtk(self):
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.setCentralWidget(self.vtk_widget)

        self.power = 500
        self.length = 1.0
        self.num_points = 100
        self.pressure = np.zeros(self.num_points)
        self.resistance = np.zeros(self.num_points)
        self.middle_index = self.num_points // 2
        self.max_pressure = self.power / self.length
        self.pressure[self.middle_index] = self.max_pressure

        for i in range(self.middle_index):
            self.pressure[i] = self.max_pressure * (1 - i / self.middle_index)
            self.resistance[i] = self.pressure[i] * self.length / self.power

        for i in range(self.middle_index, self.num_points):
            self.pressure[i] = self.max_pressure * (1 - (self.num_points - i) / self.middle_index)
            self.resistance[i] = self.pressure[i] * self.length / self.power

        self.append_filter = vtk.vtkAppendPolyData()
        self.delta_x = self.length / self.num_points

        self.cube_source_wall_left = vtk.vtkCubeSource()
        self.cube_source_wall_left.SetXLength(0.2)
        self.cube_source_wall_left.SetYLength(0.05)
        self.cube_source_wall_left.SetZLength(0.2)
        self.cube_source_wall_left.SetCenter(0, 0.0, 0.0)
        self.cube_source_wall_left.Update()
        self.append_filter.AddInputData(self.cube_source_wall_left.GetOutput())

        self.cube_source_wall_right = vtk.vtkCubeSource()
        self.cube_source_wall_right.SetXLength(0.2)
        self.cube_source_wall_right.SetYLength(0.05)
        self.cube_source_wall_right.SetZLength(0.2)
        self.cube_source_wall_right.SetCenter(0, 1.01, 0.0)
        self.cube_source_wall_right.Update()
        self.append_filter.AddInputData(self.cube_source_wall_right.GetOutput())

        self.cube_press = vtk.vtkCubeSource()
        self.cube_press.SetXLength(0.05)
        self.cube_press.SetYLength(0.05)
        self.cube_press.SetZLength(0.05)
        self.cube_press.SetCenter(0, 0.52, 0.035)
        self.cube_press.Update()
        self.append_filter.AddInputData(self.cube_press.GetOutput())

        self.cube_floor = vtk.vtkCubeSource()
        self.cube_floor.SetXLength(1.2)
        self.cube_floor.SetYLength(1.2)
        self.cube_floor.SetZLength(0.05)
        self.cube_floor.SetCenter(0, 0.5, -0.1)
        self.cube_floor.Update()
        self.append_filter.AddInputData(self.cube_floor.GetOutput())

        for i in range(self.num_points):
            self.cylinder_source = vtk.vtkCylinderSource()
            self.cylinder_source.SetRadius(0.01)
            self.cylinder_source.SetHeight(self.delta_x)
            self.cylinder_source.SetResolution(360)
            self.cylinder_source.SetCenter(0.0, i * self.delta_x, 0.0)
            self.cylinder_source.Update()

            self.append_filter.AddInputData(self.cylinder_source.GetOutput())

        self.append_filter.Update()
        self.barre_polydata = self.append_filter.GetOutput()
        self.barre_polydata_2 = self.append_filter.GetOutput()

        self.num_barre_points = self.barre_polydata.GetNumberOfPoints()
        self.pressure_array = np.zeros(self.num_barre_points)
        self.resistance_array = np.zeros(self.num_barre_points)

        for i in range(self.num_points):
            self.cylinder_points_start_index = (i + 2) * 1440
            self.cylinder_points_end_index = (i + 3) * 1440
            self.pressure_array[self.cylinder_points_start_index:self.cylinder_points_end_index] = self.pressure[i]
            self.resistance_array[self.cylinder_points_start_index:self.cylinder_points_end_index] = self.resistance[i]

        self.vtk_pressure = numpy_support.numpy_to_vtk(self.pressure_array, deep=True, array_type=vtk.VTK_FLOAT)
        self.vtk_pressure.SetName('Pressure')

        self.vtk_resistance = numpy_support.numpy_to_vtk(self.resistance_array, deep=True, array_type=vtk.VTK_FLOAT)
        self.vtk_resistance.SetName('Resistance')

        self.barre_polydata.GetPointData().SetScalars(self.vtk_pressure)
        self.barre_polydata_2.GetPointData().SetScalars(self.vtk_resistance)

        self.mapper = vtk.vtkPolyDataMapper()
        self.mapper.SetInputData(self.barre_polydata_2)
        self.mapper.SetScalarModeToUsePointData()
        self.mapper.SelectColorArray('Resistance')
        self.mapper.SetColorModeToMapScalars()
        self.mapper.SetScalarRange(np.min(self.resistance), np.max(self.resistance))

        self.barre_actor = vtk.vtkActor()
        self.barre_actor.SetMapper(self.mapper)

        self.wall_mapper = vtk.vtkPolyDataMapper()
        self.wall_mapper.SetInputData(self.cube_source_wall_left.GetOutput())

        self.wall_actor = vtk.vtkActor()
        self.wall_actor.SetMapper(self.wall_mapper)
        self.wall_actor.GetProperty().SetColor(0.5, 0.5, 0.5)

        self.wall_mapper_right = vtk.vtkPolyDataMapper()
        self.wall_mapper_right.SetInputData(self.cube_source_wall_right.GetOutput())

        self.wall_actor_right = vtk.vtkActor()
        self.wall_actor_right.SetMapper(self.wall_mapper_right)
        self.wall_actor_right.GetProperty().SetColor(0.5, 0.5, 0.5)

        self.floor_mapper = vtk.vtkPolyDataMapper()
        self.floor_mapper.SetInputData(self.cube_floor.GetOutput())

        self.floor_actor = vtk.vtkActor()
        self.floor_actor.SetMapper(self.floor_mapper)
        self.floor_actor.GetProperty().SetColor(1, 1, 1)

        self.piece_mapper = vtk.vtkPolyDataMapper()
        self.piece_mapper.SetInputData(self.cube_press.GetOutput())

        self.piece_actor = vtk.vtkActor()
        self.piece_actor.SetMapper(self.piece_mapper)
        self.piece_actor.GetProperty().SetColor(0.28, 0.001, 0.000003)

        self.axes = vtk.vtkAxesActor()

        self.color_bar = vtk.vtkScalarBarActor()
        self.color_bar.SetLookupTable(self.mapper.GetLookupTable())
        self.color_bar.SetTitle("Resistance")
        self.color_bar.SetNumberOfLabels(5)
        self.color_bar.SetPosition(0.8, 0.1)
        self.color_bar.SetWidth(0.1)
        self.color_bar.SetHeight(0.6)

        self.renderer = vtk.vtkRenderer()
        self.renderer.AddActor(self.barre_actor)
        self.renderer.AddActor(self.wall_actor)
        self.renderer.AddActor(self.wall_actor_right)
        self.renderer.AddActor(self.piece_actor)
        self.renderer.AddActor(self.floor_actor)
        # renderer.AddActor(axes)
        self.renderer.AddActor2D(self.color_bar)
        self.renderer.SetBackground(0.2, 0.3, 0.4)

        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.vtk_widget.Initialize()

        self.button = QtWidgets.QPushButton('Switch Data', self)
        self.button.setGeometry(10, 10, 100, 30)
        self.button.clicked.connect(self.switch_data)

        self.show()

        self.switcher = 1

    def switch_data(self):
        global barre_polydata, barre_polydata_2, mapper, color_bar

        # Swap the input data
        if self.mapper.GetInputDataObject(0, self.switcher) == self.barre_polydata:
            self.mapper.SetInputData(self.barre_polydata_2)
            self.mapper.SetScalarModeToUsePointData()
            self.mapper.SelectColorArray('Resistance')
            self.mapper.SetColorModeToMapScalars()
            self.mapper.SetScalarRange(np.min(self.resistance), np.max(self.resistance))
            print("yes 1")
        else :
            self.mapper.SetInputData(self.barre_polydata)
            self.mapper.SetScalarModeToUsePointData()
            self.mapper.SelectColorArray('Pressure')
            self.mapper.SetColorModeToMapScalars()
            self.mapper.SetScalarRange(np.min(self.pressure), np.max(self.pressure))
            print(self.pressure)
            print("yes 2")

        self.switcher = 1 - self.switcher

        print(self.switcher)

        self.vtk_widget = self.centralWidget()
        self.vtk_widget.GetRenderWindow().Render()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
